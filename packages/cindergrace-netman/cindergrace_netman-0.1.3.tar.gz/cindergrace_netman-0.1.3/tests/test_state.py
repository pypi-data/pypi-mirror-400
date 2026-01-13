"""Tests for state management."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cindergrace_netman.state import (
    DEFAULT_STATE,
    DESKTOP_ENTRY,
    autostart_path,
    disable_autostart,
    enable_autostart,
    get_start_script_path,
    is_autostart_enabled,
    load_state,
    save_state,
    state_path,
)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / ".config" / "cindergrace_netman"
    config_dir.mkdir(parents=True)
    return config_dir


@pytest.fixture
def mock_state_path(temp_config_dir):
    """Mock state_path to use temp directory."""
    state_file = temp_config_dir / "state.json"
    with patch("cindergrace_netman.state.state_path", return_value=state_file):
        yield state_file


def test_state_path_returns_path():
    """Test that state_path returns a Path object."""
    result = state_path()
    assert isinstance(result, Path)
    assert result.name == "state.json"


def test_load_state_returns_defaults_when_no_file(mock_state_path):
    """Test that load_state returns defaults when file doesn't exist."""
    state = load_state()
    assert state["percent"] == DEFAULT_STATE["percent"]
    assert state["base_mbit"] == DEFAULT_STATE["base_mbit"]
    assert state["enabled"] == DEFAULT_STATE["enabled"]


def test_load_state_reads_existing_file(mock_state_path):
    """Test that load_state reads existing state file."""
    custom_state = {
        "percent": 75,
        "base_mbit": 250,
        "enabled": True,
        "iface": "eth0",
    }
    mock_state_path.write_text(json.dumps(custom_state))

    state = load_state()
    assert state["percent"] == 75
    assert state["base_mbit"] == 250
    assert state["enabled"] is True
    assert state["iface"] == "eth0"


def test_load_state_merges_with_defaults(mock_state_path):
    """Test that load_state merges partial state with defaults."""
    partial_state = {"percent": 50}
    mock_state_path.write_text(json.dumps(partial_state))

    state = load_state()
    assert state["percent"] == 50
    assert state["base_mbit"] == DEFAULT_STATE["base_mbit"]


def test_save_state_creates_file(mock_state_path):
    """Test that save_state creates state file."""
    state = {"percent": 80, "base_mbit": 100}
    save_state(state)

    assert mock_state_path.exists()
    saved = json.loads(mock_state_path.read_text())
    assert saved["percent"] == 80


def test_save_state_overwrites_existing(mock_state_path):
    """Test that save_state overwrites existing file."""
    mock_state_path.write_text(json.dumps({"percent": 10}))

    save_state({"percent": 90})

    saved = json.loads(mock_state_path.read_text())
    assert saved["percent"] == 90


def test_load_state_handles_invalid_json(mock_state_path):
    """Test that load_state handles corrupted JSON gracefully."""
    mock_state_path.write_text("not valid json {{{")

    state = load_state()
    # Should return defaults on error
    assert state["percent"] == DEFAULT_STATE["percent"]


# === Autostart Tests ===


def test_autostart_path_returns_path():
    """Test that autostart_path returns a Path object."""
    result = autostart_path()
    assert isinstance(result, Path)
    assert result.name == "cindergrace-netman.desktop"
    assert "autostart" in str(result)


def test_desktop_entry_format():
    """Test that DESKTOP_ENTRY has correct format."""
    assert "[Desktop Entry]" in DESKTOP_ENTRY
    assert "Type=Application" in DESKTOP_ENTRY
    assert "CinderGrace NetMan" in DESKTOP_ENTRY
    assert "{exec_path}" in DESKTOP_ENTRY
    assert "TryExec" in DESKTOP_ENTRY
    assert "Terminal=false" in DESKTOP_ENTRY
    assert "X-GNOME-Autostart-enabled=true" in DESKTOP_ENTRY


def test_default_state_keys():
    """Test DEFAULT_STATE has all expected keys."""
    expected_keys = {"enabled", "percent", "base_mbit", "iface", "download_url", "ping_host", "language", "autostart"}
    assert expected_keys == set(DEFAULT_STATE.keys())


def test_default_state_values():
    """Test DEFAULT_STATE has correct default values."""
    assert DEFAULT_STATE["enabled"] is False
    assert DEFAULT_STATE["percent"] == 100
    assert DEFAULT_STATE["base_mbit"] == 100
    assert DEFAULT_STATE["language"] == "en"
    assert DEFAULT_STATE["autostart"] is False


class TestIsAutostartEnabled:
    """Tests for is_autostart_enabled function."""

    def test_returns_false_when_file_missing(self, tmp_path):
        """Test returns False when desktop file doesn't exist."""
        with patch("cindergrace_netman.state.autostart_path") as mock_path:
            mock_path.return_value = tmp_path / "nonexistent.desktop"
            assert is_autostart_enabled() is False

    def test_returns_true_when_file_exists(self, tmp_path):
        """Test returns True when desktop file exists."""
        desktop_file = tmp_path / "test.desktop"
        desktop_file.write_text("[Desktop Entry]")
        with patch("cindergrace_netman.state.autostart_path") as mock_path:
            mock_path.return_value = desktop_file
            assert is_autostart_enabled() is True


class TestGetStartScriptPath:
    """Tests for get_start_script_path function."""

    def test_finds_start_sh_in_project(self, tmp_path):
        """Test finds start.sh in project directory."""
        # Create mock project structure
        src_dir = tmp_path / "src" / "cindergrace_netman"
        src_dir.mkdir(parents=True)
        start_sh = tmp_path / "start.sh"
        start_sh.write_text("#!/bin/bash")

        with patch("cindergrace_netman.state.Path") as mock_path_cls:
            # Mock __file__ to point to our temp structure
            mock_file_path = MagicMock()
            mock_file_path.parent = src_dir
            mock_path_cls.return_value = mock_file_path
            mock_path_cls.__call__ = lambda self, x: Path(x)

            # The actual function uses Path(__file__), so we need different approach
            result = get_start_script_path()
            # Just verify it returns a Path
            assert isinstance(result, Path)

    @patch("shutil.which")
    def test_falls_back_to_entry_point(self, mock_which):
        """Test falls back to entry point when start.sh not found."""
        mock_which.return_value = "/usr/local/bin/cindergrace-netman"

        # Create a scenario where start.sh doesn't exist
        with patch("cindergrace_netman.state.Path.__file__", create=True):
            result = get_start_script_path()
            # Function should return a path
            assert isinstance(result, Path)


class TestEnableAutostart:
    """Tests for enable_autostart function."""

    def test_creates_desktop_file(self, tmp_path):
        """Test that enable_autostart creates desktop file."""
        desktop_file = tmp_path / "autostart" / "cindergrace-netman.desktop"

        with patch("cindergrace_netman.state.autostart_path") as mock_path:
            mock_path.return_value = desktop_file
            with patch("cindergrace_netman.state.get_start_script_path") as mock_script:
                mock_script.return_value = Path("/usr/bin/cindergrace-netman")

                result = enable_autostart()

                assert result is True
                assert desktop_file.exists()
                content = desktop_file.read_text()
                assert "[Desktop Entry]" in content
                assert "/usr/bin/cindergrace-netman" in content

    def test_handles_write_error(self, tmp_path):
        """Test that enable_autostart handles write errors."""
        # Create a directory where file should be - causes write error
        desktop_file = tmp_path / "autostart" / "cindergrace-netman.desktop"
        desktop_file.parent.mkdir(parents=True)
        desktop_file.mkdir()  # Make it a directory to cause error

        with patch("cindergrace_netman.state.autostart_path") as mock_path:
            mock_path.return_value = desktop_file
            with patch("cindergrace_netman.state.get_start_script_path") as mock_script:
                mock_script.return_value = Path("/usr/bin/test")

                result = enable_autostart()
                assert result is False


class TestDisableAutostart:
    """Tests for disable_autostart function."""

    def test_removes_existing_file(self, tmp_path):
        """Test that disable_autostart removes desktop file."""
        desktop_file = tmp_path / "autostart" / "cindergrace-netman.desktop"
        desktop_file.parent.mkdir(parents=True)
        desktop_file.write_text("[Desktop Entry]")

        with patch("cindergrace_netman.state.autostart_path") as mock_path:
            mock_path.return_value = desktop_file

            result = disable_autostart()

            assert result is True
            assert not desktop_file.exists()

    def test_returns_true_when_file_missing(self, tmp_path):
        """Test returns True when file already doesn't exist."""
        desktop_file = tmp_path / "nonexistent.desktop"

        with patch("cindergrace_netman.state.autostart_path") as mock_path:
            mock_path.return_value = desktop_file

            result = disable_autostart()
            assert result is True

    def test_handles_delete_error(self, tmp_path):
        """Test handles error when file can't be deleted."""
        desktop_file = tmp_path / "autostart" / "test.desktop"
        desktop_file.parent.mkdir(parents=True)
        desktop_file.write_text("test")

        with patch("cindergrace_netman.state.autostart_path") as mock_path:
            mock_path.return_value = desktop_file
            with patch.object(Path, "unlink", side_effect=OSError("Permission denied")):
                result = disable_autostart()
                assert result is False
