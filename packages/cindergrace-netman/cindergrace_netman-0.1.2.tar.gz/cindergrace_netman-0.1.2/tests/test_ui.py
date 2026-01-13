"""Tests for UI helper functions."""

from unittest.mock import patch


def test_get_tab_labels_english():
    """Test tab labels for English."""
    from cindergrace_netman.ui import _get_tab_labels

    network, settings = _get_tab_labels("en")
    assert network == "Network"
    assert settings == "Settings"


def test_get_tab_labels_german():
    """Test tab labels for German."""
    from cindergrace_netman.ui import _get_tab_labels

    network, settings = _get_tab_labels("de")
    assert network == "Netzwerk"
    assert settings == "Einstellungen"


def test_get_tab_labels_unknown_defaults_to_english():
    """Test that unknown language defaults to English."""
    from cindergrace_netman.ui import _get_tab_labels

    network, settings = _get_tab_labels("fr")
    assert network == "Network"
    assert settings == "Settings"


def test_get_default_interface_value_from_state():
    """Test getting interface from state."""
    from cindergrace_netman.ui import _get_default_interface_value

    state = {"iface": "eth0"}
    result = _get_default_interface_value(state, ["wlan0", "eth1"])
    assert result == "eth0"


def test_get_default_interface_value_from_system():
    """Test getting interface from system when not in state."""
    from cindergrace_netman.ui import _get_default_interface_value

    with patch("cindergrace_netman.ui.get_default_interface", return_value="wlan0"):
        state = {"iface": None}
        result = _get_default_interface_value(state, ["eth0", "wlan0"])
        assert result == "wlan0"


def test_get_default_interface_value_fallback_to_list():
    """Test fallback to first interface in list."""
    from cindergrace_netman.ui import _get_default_interface_value

    with patch("cindergrace_netman.ui.get_default_interface", return_value=None):
        state = {"iface": None}
        result = _get_default_interface_value(state, ["eth0", "wlan0"])
        assert result == "eth0"


def test_get_default_interface_value_empty_list():
    """Test with empty interface list."""
    from cindergrace_netman.ui import _get_default_interface_value

    with patch("cindergrace_netman.ui.get_default_interface", return_value=None):
        state = {"iface": None}
        result = _get_default_interface_value(state, [])
        assert result == ""


def test_get_toggle_button_props_enabled():
    """Test toggle button props when limit is enabled."""
    from cindergrace_netman.ui import _get_toggle_button_props

    with patch("cindergrace_netman.ui._", side_effect=lambda x: x):
        label, variant = _get_toggle_button_props(True)
        assert label == "disable_limit"
        assert variant == "stop"


def test_get_toggle_button_props_disabled():
    """Test toggle button props when limit is disabled."""
    from cindergrace_netman.ui import _get_toggle_button_props

    with patch("cindergrace_netman.ui._", side_effect=lambda x: x):
        label, variant = _get_toggle_button_props(False)
        assert label == "enable_limit"
        assert variant == "primary"


def test_get_autostart_button_props_enabled():
    """Test autostart button props when enabled."""
    from cindergrace_netman.ui import _get_autostart_button_props

    with patch("cindergrace_netman.ui._", side_effect=lambda x: x):
        label, variant = _get_autostart_button_props(True)
        assert label == "autostart_enabled"
        assert variant == "stop"


def test_get_autostart_button_props_disabled():
    """Test autostart button props when disabled."""
    from cindergrace_netman.ui import _get_autostart_button_props

    with patch("cindergrace_netman.ui._", side_effect=lambda x: x):
        label, variant = _get_autostart_button_props(False)
        assert label == "autostart_disabled"
        assert variant == "primary"


def test_get_interface_choices_returns_list():
    """Test that interface choices returns a list of tuples."""
    from cindergrace_netman.ui import _get_interface_choices

    mock_interfaces = [
        {"name": "eth0", "speed_mbit": 1000, "state": "up", "is_default": True},
        {"name": "wlan0", "speed_mbit": 150, "state": "up", "is_default": False},
    ]

    with patch(
        "cindergrace_netman.ui.list_interfaces_with_info", return_value=mock_interfaces
    ):
        choices = _get_interface_choices()

        assert len(choices) == 2
        assert all(isinstance(c, tuple) for c in choices)
        assert all(len(c) == 2 for c in choices)
        # First tuple: (label, value)
        assert choices[0][1] == "eth0"
        assert choices[1][1] == "wlan0"


def test_get_interface_choices_includes_status_markers():
    """Test that interface labels include status markers."""
    from cindergrace_netman.ui import _get_interface_choices

    mock_interfaces = [
        {"name": "eth0", "speed_mbit": 1000, "state": "up", "is_default": True},
    ]

    with patch(
        "cindergrace_netman.ui.list_interfaces_with_info", return_value=mock_interfaces
    ):
        choices = _get_interface_choices()
        label = choices[0][0]

        assert "eth0" in label
        assert "1000 Mbit/s" in label
        assert "✓" in label  # up state
        assert "⬤" in label  # default route
