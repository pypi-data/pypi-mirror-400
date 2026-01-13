"""Tests for network utilities."""

from unittest.mock import MagicMock, patch

import pytest

from cindergrace_netman.net import (
    NetmanError,
    _run,
    _run_ignore,
    _setup_ifb,
    apply_limit,
    clear_limit,
    get_default_interface,
    get_interface_speed,
    get_interface_state,
    list_interfaces,
    list_interfaces_with_info,
)


class TestListInterfaces:
    """Tests for list_interfaces function."""

    def test_returns_list(self):
        """Test that list_interfaces returns a list."""
        result = list_interfaces()
        assert isinstance(result, list)

    def test_contains_interface_names(self):
        """Test that list_interfaces returns interface name strings."""
        result = list_interfaces()
        # All entries should be non-empty strings
        for iface in result:
            assert isinstance(iface, str)
            assert len(iface) > 0


class TestGetDefaultInterface:
    """Tests for get_default_interface function."""

    def test_returns_string_or_none(self):
        """Test that get_default_interface returns string or None."""
        result = get_default_interface()
        assert result is None or isinstance(result, str)


class TestGetInterfaceState:
    """Tests for get_interface_state function."""

    def test_returns_valid_state(self):
        """Test that get_interface_state returns valid state."""
        # Use an existing interface if possible
        interfaces = list_interfaces()
        if interfaces:
            state = get_interface_state(interfaces[0])
            assert state in ["up", "down", "unknown"]

    def test_unknown_interface_returns_unknown(self):
        """Test that unknown interface returns 'unknown'."""
        state = get_interface_state("nonexistent_iface_xyz")
        assert state == "unknown"


class TestGetInterfaceSpeed:
    """Tests for get_interface_speed function."""

    def test_returns_int_or_none(self):
        """Test that get_interface_speed returns int or None."""
        interfaces = list_interfaces()
        if interfaces:
            speed = get_interface_speed(interfaces[0])
            assert speed is None or isinstance(speed, int)

    def test_unknown_interface_returns_none(self):
        """Test that unknown interface returns None."""
        speed = get_interface_speed("nonexistent_iface_xyz")
        assert speed is None


class TestListInterfacesWithInfo:
    """Tests for list_interfaces_with_info function."""

    def test_returns_list_of_dicts(self):
        """Test that list_interfaces_with_info returns list of dicts."""
        result = list_interfaces_with_info()
        assert isinstance(result, list)
        for iface in result:
            assert isinstance(iface, dict)
            assert "name" in iface
            assert "state" in iface
            assert "speed_mbit" in iface
            assert "is_default" in iface

    def test_interface_info_structure(self):
        """Test that interface info has correct structure."""
        result = list_interfaces_with_info()
        if result:
            iface = result[0]
            assert isinstance(iface["name"], str)
            assert iface["state"] in ["up", "down", "unknown"]
            assert iface["speed_mbit"] is None or isinstance(iface["speed_mbit"], int)
            assert isinstance(iface["is_default"], bool)


class TestNetmanError:
    """Tests for NetmanError exception."""

    def test_netman_error_is_exception(self):
        """Test that NetmanError is an Exception."""
        error = NetmanError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"

    def test_can_raise_and_catch(self):
        """Test that NetmanError can be raised and caught."""
        with pytest.raises(NetmanError):
            raise NetmanError("test")


class TestRun:
    """Tests for _run helper function."""

    @patch("cindergrace_netman.net.subprocess.run")
    def test_run_returns_output(self, mock_run):
        """Test that _run returns command output."""
        mock_result = MagicMock()
        mock_result.stdout = "output text\n"
        mock_run.return_value = mock_result
        result = _run(["echo", "test"])
        assert result == "output text"

    @patch("cindergrace_netman.net.subprocess.run")
    def test_run_raises_on_error(self, mock_run):
        """Test that _run raises NetmanError on CalledProcessError."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="error message")
        with pytest.raises(NetmanError, match="error message"):
            _run(["false"])

    @patch("cindergrace_netman.net.subprocess.run")
    def test_run_raises_with_fallback_message(self, mock_run):
        """Test that _run uses fallback message when stderr is empty."""
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="")
        with pytest.raises(NetmanError, match="Command failed"):
            _run(["false"])


class TestRunIgnore:
    """Tests for _run_ignore helper function."""

    @patch("cindergrace_netman.net._run")
    def test_run_ignore_calls_run(self, mock_run):
        """Test that _run_ignore calls _run."""
        _run_ignore(["echo", "test"])
        mock_run.assert_called_once_with(["echo", "test"])

    @patch("cindergrace_netman.net._run")
    def test_run_ignore_ignores_errors(self, mock_run):
        """Test that _run_ignore ignores NetmanError."""
        mock_run.side_effect = NetmanError("error")
        # Should not raise, should return None
        result = _run_ignore(["false"])
        assert result is None


class TestSetupIfb:
    """Tests for _setup_ifb function."""

    @patch("cindergrace_netman.net._run")
    @patch("cindergrace_netman.net._run_ignore")
    def test_setup_ifb_calls_commands(self, mock_run_ignore, mock_run):
        """Test that _setup_ifb calls correct commands."""
        _setup_ifb()

        # Should call modprobe and ip link add (ignored)
        assert mock_run_ignore.call_count == 2

        # Should call ip link set up
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "ip" in args
        assert "link" in args
        assert "up" in args


class TestApplyLimit:
    """Tests for apply_limit function."""

    def test_raises_on_zero_rate(self):
        """Test that apply_limit raises on zero rate."""
        with pytest.raises(NetmanError, match="Rate must be > 0"):
            apply_limit("eth0", 0)

    def test_raises_on_negative_rate(self):
        """Test that apply_limit raises on negative rate."""
        with pytest.raises(NetmanError, match="Rate must be > 0"):
            apply_limit("eth0", -5)

    @patch("cindergrace_netman.net._run")
    @patch("cindergrace_netman.net._run_ignore")
    @patch("cindergrace_netman.net._setup_ifb")
    def test_apply_limit_calls_tc_commands(self, mock_setup, mock_run_ignore, mock_run):
        """Test that apply_limit calls tc commands."""
        apply_limit("eth0", 50.0)

        mock_setup.assert_called_once()
        # Multiple tc commands should be called
        assert mock_run.call_count >= 3

    @patch("cindergrace_netman.net._run")
    @patch("cindergrace_netman.net._run_ignore")
    @patch("cindergrace_netman.net._setup_ifb")
    def test_apply_limit_formats_rate_correctly(self, mock_setup, mock_run_ignore, mock_run):
        """Test that rate is formatted correctly without trailing zeros."""
        apply_limit("eth0", 50.0)

        # Check that one of the calls contains the rate
        calls = [str(call) for call in mock_run.call_args_list]
        rate_call = [c for c in calls if "mbit" in c]
        assert len(rate_call) > 0
        # Should be "50mbit" not "50.00mbit"
        assert "50mbit" in str(rate_call[0])


class TestClearLimit:
    """Tests for clear_limit function."""

    @patch("cindergrace_netman.net._run_ignore")
    def test_clear_limit_calls_cleanup_commands(self, mock_run_ignore):
        """Test that clear_limit calls cleanup commands."""
        clear_limit("eth0")

        # Should call multiple cleanup commands
        assert mock_run_ignore.call_count == 5

    @patch("cindergrace_netman.net._run_ignore")
    def test_clear_limit_with_different_interface(self, mock_run_ignore):
        """Test clear_limit with different interface name."""
        clear_limit("wlan0")

        # Verify interface name is used in calls
        calls_str = str(mock_run_ignore.call_args_list)
        assert "wlan0" in calls_str
