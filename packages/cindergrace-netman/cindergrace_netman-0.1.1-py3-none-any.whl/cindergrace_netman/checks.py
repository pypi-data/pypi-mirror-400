import re
import time
import urllib.request

from .net import NetmanError, _run


def ping(host: str, count: int = 4, interval: float = 0.2) -> dict:
    output = _run(["ping", "-c", str(count), "-i", str(interval), host])
    summary = {
        "transmitted": None,
        "received": None,
        "loss_percent": None,
        "min_ms": None,
        "avg_ms": None,
        "max_ms": None,
        "mdev_ms": None,
    }
    for line in output.splitlines():
        if "packets transmitted" in line:
            match = re.search(
                r"(?P<tx>\d+) packets transmitted, (?P<rx>\d+) received, "
                r"(?P<loss>\d+)% packet loss",
                line,
            )
            if match:
                summary["transmitted"] = int(match.group("tx"))
                summary["received"] = int(match.group("rx"))
                summary["loss_percent"] = int(match.group("loss"))
        if "min/avg/max" in line:
            match = re.search(
                r"=\s*(?P<min>[\d.]+)/(?P<avg>[\d.]+)/(?P<max>[\d.]+)/(?P<mdev>[\d.]+)",
                line,
            )
            if match:
                summary["min_ms"] = float(match.group("min"))
                summary["avg_ms"] = float(match.group("avg"))
                summary["max_ms"] = float(match.group("max"))
                summary["mdev_ms"] = float(match.group("mdev"))
    return summary


def download_test(url: str, max_mb: int = 10) -> dict:
    # Security: Only allow http/https URLs to prevent SSRF via file:// etc.
    if not url.lower().startswith(("http://", "https://")):
        raise NetmanError(f"Invalid URL scheme - only http/https allowed: {url}")

    max_bytes = max_mb * 1024 * 1024
    start = time.monotonic()
    bytes_read = 0
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            while bytes_read < max_bytes:
                chunk = response.read(min(1024 * 256, max_bytes - bytes_read))
                if not chunk:
                    break
                bytes_read += len(chunk)
    except Exception as exc:  # noqa: BLE001 - surface network errors to caller
        raise NetmanError(str(exc)) from exc
    elapsed = max(time.monotonic() - start, 0.001)
    mbit_per_s = (bytes_read * 8) / (elapsed * 1_000_000)
    return {
        "bytes_read": bytes_read,
        "elapsed_s": elapsed,
        "mbit_per_s": mbit_per_s,
    }
