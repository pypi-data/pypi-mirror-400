"""Tests for tray module."""

from unittest.mock import MagicMock, patch

from PIL import Image

from cindergrace_netman.tray import _make_icon, _tooltip, run_tray


class TestMakeIcon:
    """Tests for _make_icon function."""

    def test_returns_image_when_enabled(self):
        """Test that _make_icon returns an Image when enabled."""
        result = _make_icon(enabled=True)
        assert isinstance(result, Image.Image)
        assert result.size == (64, 64)
        assert result.mode == "RGBA"

    def test_returns_image_when_disabled(self):
        """Test that _make_icon returns an Image when disabled."""
        result = _make_icon(enabled=False)
        assert isinstance(result, Image.Image)
        assert result.size == (64, 64)

    def test_different_colors_for_states(self):
        """Test that enabled and disabled have different colors."""
        enabled_icon = _make_icon(enabled=True)
        disabled_icon = _make_icon(enabled=False)

        # Get center pixel color (inside the circle)
        enabled_pixel = enabled_icon.getpixel((32, 32))
        disabled_pixel = disabled_icon.getpixel((32, 32))

        # Colors should be different
        assert enabled_pixel != disabled_pixel


class TestTooltip:
    """Tests for _tooltip function."""

    def test_tooltip_active_state(self):
        """Test tooltip text for active state."""
        state = {
            "enabled": True,
            "percent": 50,
            "base_mbit": 100,
        }
        result = _tooltip(state, "eth0")

        assert "aktiv" in result
        assert "50%" in result
        assert "50.00" in result  # 50% of 100 = 50.00 Mbit/s
        assert "eth0" in result

    def test_tooltip_inactive_state(self):
        """Test tooltip text for inactive state."""
        state = {
            "enabled": False,
            "percent": 100,
            "base_mbit": 100,
        }
        result = _tooltip(state, "wlan0")

        assert "aus" in result
        assert "100%" in result
        assert "wlan0" in result

    def test_tooltip_no_interface(self):
        """Test tooltip text when no interface specified."""
        state = {
            "enabled": False,
            "percent": 75,
            "base_mbit": 200,
        }
        result = _tooltip(state, None)

        assert "?" in result
        assert "75%" in result
        # 75% of 200 = 150.00 Mbit/s
        assert "150.00" in result

    def test_tooltip_rate_calculation(self):
        """Test that rate is calculated correctly."""
        state = {
            "enabled": True,
            "percent": 25,
            "base_mbit": 400,
        }
        result = _tooltip(state, "eth0")

        # 25% of 400 = 100.00 Mbit/s
        assert "100.00" in result


class TestRunTray:
    """Tests for run_tray function."""

    @patch("cindergrace_netman.tray.pystray.Icon")
    @patch("cindergrace_netman.tray.get_default_interface")
    @patch("cindergrace_netman.tray.load_state")
    def test_run_tray_creates_icon(self, mock_load, mock_get_iface, mock_icon_class):
        """Test that run_tray creates and runs an icon."""
        mock_load.return_value = {
            "enabled": False,
            "percent": 100,
            "base_mbit": 100,
            "iface": None,
        }
        mock_get_iface.return_value = "eth0"
        mock_icon = MagicMock()
        mock_icon_class.return_value = mock_icon

        run_tray()

        mock_icon_class.assert_called_once()
        mock_icon.run.assert_called_once()

    @patch("cindergrace_netman.tray.pystray.Icon")
    @patch("cindergrace_netman.tray.get_default_interface")
    @patch("cindergrace_netman.tray.load_state")
    def test_run_tray_with_existing_iface(self, mock_load, mock_get_iface, mock_icon_class):
        """Test run_tray when interface is already set in state."""
        mock_load.return_value = {
            "enabled": True,
            "percent": 75,
            "base_mbit": 200,
            "iface": "wlan0",
        }
        mock_icon = MagicMock()
        mock_icon_class.return_value = mock_icon

        run_tray()

        # Should not need to get default interface
        mock_icon.run.assert_called_once()
