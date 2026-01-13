"""Tests for CLI module."""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from cindergrace_netman.cli import (
    _cmd_clear,
    _cmd_download,
    _cmd_limit,
    _cmd_ping,
    _cmd_status,
    _resolve_iface,
    build_parser,
    main,
)
from cindergrace_netman.net import NetmanError


class TestResolveIface:
    """Tests for _resolve_iface function."""

    def test_returns_provided_iface(self):
        """Test that provided iface is returned as-is."""
        result = _resolve_iface("eth0")
        assert result == "eth0"

    def test_returns_provided_iface_wlan(self):
        """Test that provided wlan iface is returned."""
        result = _resolve_iface("wlan0")
        assert result == "wlan0"

    @patch("cindergrace_netman.cli.get_default_interface")
    def test_detects_default_when_none(self, mock_get_default):
        """Test that default interface is detected when none provided."""
        mock_get_default.return_value = "enp0s3"
        result = _resolve_iface(None)
        assert result == "enp0s3"
        mock_get_default.assert_called_once()

    @patch("cindergrace_netman.cli.get_default_interface")
    def test_raises_when_no_default_found(self, mock_get_default):
        """Test that NetmanError is raised when no default found."""
        mock_get_default.return_value = None
        with pytest.raises(NetmanError, match="No default interface"):
            _resolve_iface(None)


class TestBuildParser:
    """Tests for build_parser function."""

    def test_returns_parser(self):
        """Test that parser is returned."""
        parser = build_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_ui_command_defaults(self):
        """Test UI command default values."""
        parser = build_parser()
        args = parser.parse_args(["ui"])
        assert args.command == "ui"
        assert args.host == "127.0.0.1"
        assert args.port == 7863
        assert args.share is False

    def test_ui_command_custom_values(self):
        """Test UI command with custom values."""
        parser = build_parser()
        args = parser.parse_args(["ui", "--host", "0.0.0.0", "--port", "8080", "--share"])
        assert args.host == "0.0.0.0"
        assert args.port == 8080
        assert args.share is True

    def test_limit_command_defaults(self):
        """Test limit command default values."""
        parser = build_parser()
        args = parser.parse_args(["limit"])
        assert args.command == "limit"
        assert args.percent == 100
        assert args.base_mbit == 100
        assert args.iface is None

    def test_limit_command_custom_values(self):
        """Test limit command with custom values."""
        parser = build_parser()
        args = parser.parse_args(["limit", "--percent", "50", "--base-mbit", "200", "--iface", "eth0"])
        assert args.percent == 50
        assert args.base_mbit == 200
        assert args.iface == "eth0"

    def test_clear_command(self):
        """Test clear command."""
        parser = build_parser()
        args = parser.parse_args(["clear"])
        assert args.command == "clear"
        assert args.iface is None

    def test_clear_command_with_iface(self):
        """Test clear command with interface."""
        parser = build_parser()
        args = parser.parse_args(["clear", "--iface", "wlan0"])
        assert args.iface == "wlan0"

    def test_status_command(self):
        """Test status command."""
        parser = build_parser()
        args = parser.parse_args(["status"])
        assert args.command == "status"

    def test_ping_command_defaults(self):
        """Test ping command default values."""
        parser = build_parser()
        args = parser.parse_args(["ping"])
        assert args.command == "ping"
        assert args.host == "8.8.8.8"
        assert args.count == 4
        assert args.interval == 0.2

    def test_ping_command_custom_values(self):
        """Test ping command with custom values."""
        parser = build_parser()
        args = parser.parse_args(["ping", "--host", "1.1.1.1", "--count", "10", "--interval", "0.5"])
        assert args.host == "1.1.1.1"
        assert args.count == 10
        assert args.interval == 0.5

    def test_download_command_defaults(self):
        """Test download command default values."""
        parser = build_parser()
        args = parser.parse_args(["download"])
        assert args.command == "download"
        assert "hetzner" in args.url
        assert args.max_mb == 10

    def test_download_command_custom_values(self):
        """Test download command with custom values."""
        parser = build_parser()
        args = parser.parse_args(["download", "--url", "https://example.com/file", "--max-mb", "5"])
        assert args.url == "https://example.com/file"
        assert args.max_mb == 5

    def test_tray_command(self):
        """Test tray command."""
        parser = build_parser()
        args = parser.parse_args(["tray"])
        assert args.command == "tray"


class TestCmdLimit:
    """Tests for _cmd_limit function."""

    @patch("cindergrace_netman.cli.save_state")
    @patch("cindergrace_netman.cli.load_state")
    @patch("cindergrace_netman.cli.apply_limit")
    @patch("cindergrace_netman.cli._resolve_iface")
    def test_applies_limit_and_saves_state(self, mock_resolve, mock_apply, mock_load, mock_save, capsys):
        """Test that limit is applied and state saved."""
        mock_resolve.return_value = "eth0"
        mock_load.return_value = {"enabled": False, "percent": 100, "base_mbit": 100, "iface": None}

        args = argparse.Namespace(iface=None, percent=50, base_mbit=100)
        _cmd_limit(args)

        mock_apply.assert_called_once_with("eth0", 50.0)
        mock_save.assert_called_once()
        saved_state = mock_save.call_args[0][0]
        assert saved_state["enabled"] is True
        assert saved_state["percent"] == 50
        assert saved_state["iface"] == "eth0"

        captured = capsys.readouterr()
        assert "50%" in captured.out
        assert "eth0" in captured.out


class TestCmdClear:
    """Tests for _cmd_clear function."""

    @patch("cindergrace_netman.cli.save_state")
    @patch("cindergrace_netman.cli.load_state")
    @patch("cindergrace_netman.cli.clear_limit")
    @patch("cindergrace_netman.cli._resolve_iface")
    def test_clears_limit_and_saves_state(self, mock_resolve, mock_clear, mock_load, mock_save, capsys):
        """Test that limit is cleared and state saved."""
        mock_resolve.return_value = "eth0"
        mock_load.return_value = {"enabled": True, "percent": 50, "base_mbit": 100, "iface": "eth0"}

        args = argparse.Namespace(iface=None)
        _cmd_clear(args)

        mock_clear.assert_called_once_with("eth0")
        mock_save.assert_called_once()
        saved_state = mock_save.call_args[0][0]
        assert saved_state["enabled"] is False

        captured = capsys.readouterr()
        assert "disabled" in captured.out.lower()


class TestCmdStatus:
    """Tests for _cmd_status function."""

    @patch("cindergrace_netman.cli.get_default_interface")
    @patch("cindergrace_netman.cli.load_state")
    def test_shows_active_status(self, mock_load, mock_get_default, capsys):
        """Test status output when limit is active."""
        mock_load.return_value = {
            "enabled": True,
            "percent": 75,
            "base_mbit": 100,
            "iface": "eth0",
        }

        args = argparse.Namespace()
        _cmd_status(args)

        captured = capsys.readouterr()
        assert "active" in captured.out.lower()
        assert "75%" in captured.out
        assert "eth0" in captured.out

    @patch("cindergrace_netman.cli.get_default_interface")
    @patch("cindergrace_netman.cli.load_state")
    def test_shows_off_status(self, mock_load, mock_get_default, capsys):
        """Test status output when limit is off."""
        mock_load.return_value = {
            "enabled": False,
            "percent": 100,
            "base_mbit": 100,
            "iface": None,
        }
        mock_get_default.return_value = "enp0s3"

        args = argparse.Namespace()
        _cmd_status(args)

        captured = capsys.readouterr()
        assert "off" in captured.out.lower()


class TestCmdPing:
    """Tests for _cmd_ping function."""

    @patch("cindergrace_netman.cli.ping")
    def test_runs_ping_and_prints_result(self, mock_ping, capsys):
        """Test that ping is run and result printed."""
        mock_ping.return_value = {"avg_ms": 10.5, "loss_percent": 0}

        args = argparse.Namespace(host="8.8.8.8", count=4, interval=0.2)
        _cmd_ping(args)

        mock_ping.assert_called_once_with("8.8.8.8", count=4, interval=0.2)
        captured = capsys.readouterr()
        assert "avg_ms" in captured.out


class TestCmdDownload:
    """Tests for _cmd_download function."""

    @patch("cindergrace_netman.cli.download_test")
    def test_runs_download_and_prints_result(self, mock_download, capsys):
        """Test that download test is run and result printed."""
        mock_download.return_value = {"mbit_per_s": 50.5, "bytes_read": 1000000}

        args = argparse.Namespace(url="https://example.com/file", max_mb=5)
        _cmd_download(args)

        mock_download.assert_called_once_with("https://example.com/file", max_mb=5)
        captured = capsys.readouterr()
        assert "mbit_per_s" in captured.out


class TestMain:
    """Tests for main function."""

    @patch("cindergrace_netman.cli.build_parser")
    def test_main_calls_func(self, mock_build_parser):
        """Test that main calls the command function."""
        mock_func = MagicMock()
        mock_args = argparse.Namespace(func=mock_func)
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_build_parser.return_value = mock_parser

        main()

        mock_func.assert_called_once_with(mock_args)

    @patch("cindergrace_netman.cli.build_parser")
    def test_main_handles_netman_error(self, mock_build_parser):
        """Test that main handles NetmanError gracefully."""
        mock_func = MagicMock(side_effect=NetmanError("Test error"))
        mock_args = argparse.Namespace(func=mock_func)
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = mock_args
        mock_build_parser.return_value = mock_parser

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert "Test error" in str(exc_info.value)
