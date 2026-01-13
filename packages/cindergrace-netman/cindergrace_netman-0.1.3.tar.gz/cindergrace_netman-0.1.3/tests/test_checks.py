"""Tests for network checks (ping, download)."""

import pytest

from cindergrace_netman.checks import download_test, ping
from cindergrace_netman.net import NetmanError


class TestPing:
    """Tests for ping function."""

    def test_ping_localhost_succeeds(self):
        """Test that ping to localhost works."""
        result = ping("127.0.0.1", count=2, interval=0.2)

        assert "transmitted" in result
        assert "received" in result
        assert "loss_percent" in result
        assert "min_ms" in result
        assert "avg_ms" in result
        assert "max_ms" in result

    def test_ping_returns_correct_count(self):
        """Test that ping sends correct number of packets."""
        result = ping("127.0.0.1", count=3, interval=0.2)
        assert result["transmitted"] == 3

    def test_ping_localhost_has_low_loss(self):
        """Test that localhost ping has no packet loss."""
        result = ping("127.0.0.1", count=3, interval=0.2)
        assert result["loss_percent"] == 0.0

    def test_ping_times_are_numeric(self):
        """Test that ping times are numeric values."""
        result = ping("127.0.0.1", count=2, interval=0.2)
        assert isinstance(result["min_ms"], float)
        assert isinstance(result["avg_ms"], float)
        assert isinstance(result["max_ms"], float)

    def test_ping_invalid_host_raises(self):
        """Test that invalid host raises NetmanError."""
        with pytest.raises(NetmanError):
            ping("invalid.host.that.does.not.exist.example", count=1)


class TestDownloadTest:
    """Tests for download_test function."""

    def test_download_returns_metrics(self):
        """Test that download returns required metrics."""
        # Use a small, reliable test file
        result = download_test(
            "https://www.google.com/robots.txt",
            max_mb=1
        )

        assert "bytes_read" in result
        assert "elapsed_s" in result
        assert "mbit_per_s" in result

    def test_download_bytes_read_positive(self):
        """Test that download reads some bytes."""
        result = download_test(
            "https://www.google.com/robots.txt",
            max_mb=1
        )
        assert result["bytes_read"] > 0

    def test_download_elapsed_positive(self):
        """Test that elapsed time is positive."""
        result = download_test(
            "https://www.google.com/robots.txt",
            max_mb=1
        )
        assert result["elapsed_s"] > 0

    def test_download_speed_calculated(self):
        """Test that speed is calculated."""
        result = download_test(
            "https://www.google.com/robots.txt",
            max_mb=1
        )
        assert result["mbit_per_s"] >= 0

    def test_download_invalid_url_raises(self):
        """Test that invalid URL raises NetmanError."""
        with pytest.raises(NetmanError):
            download_test("https://invalid.url.that.does.not.exist.example/file")
