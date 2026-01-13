import json
import os
from pathlib import Path

DEFAULT_STATE = {
    "enabled": False,
    "percent": 100,
    "base_mbit": 100,  # DSL speed in Mbit/s
    "iface": None,
    "download_url": "https://ash-speed.hetzner.com/100MB.bin",
    "ping_host": "8.8.8.8",
    "language": "en",  # Default language (en/de)
    "autostart": False,  # Start on login
}

# XDG autostart desktop entry
DESKTOP_ENTRY = """[Desktop Entry]
Type=Application
Name=CinderGrace NetMan
Comment=Network bandwidth limiter
Exec="{exec_path}"
TryExec="{exec_path}"
Icon=network-transmit-receive
Terminal=false
Categories=Network;System;
X-GNOME-Autostart-enabled=true
"""


def state_path() -> Path:
    config_root = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    return config_root / "cindergrace_netman" / "state.json"


def load_state() -> dict:
    path = state_path()
    if not path.exists():
        return DEFAULT_STATE.copy()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return DEFAULT_STATE.copy()
    merged = DEFAULT_STATE.copy()
    merged.update({k: data.get(k, v) for k, v in DEFAULT_STATE.items()})
    return merged


def save_state(state: dict) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def autostart_path() -> Path:
    """Path to XDG autostart desktop entry."""
    config_root = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    return config_root / "autostart" / "cindergrace-netman.desktop"


def get_start_script_path() -> Path:
    """Find the start.sh script in the project directory."""
    # Try to find start.sh relative to this module
    module_dir = Path(__file__).parent
    # Go up to project root (src/cindergrace_netman -> project root)
    project_root = module_dir.parent.parent
    start_sh = project_root / "start.sh"
    if start_sh.exists():
        return start_sh
    # Fallback: check if installed via pip, use the entry point
    import shutil

    entry_point = shutil.which("cindergrace-netman")
    if entry_point:
        return Path(entry_point)
    return start_sh  # Return anyway, will show error if missing


def is_autostart_enabled() -> bool:
    """Check if autostart is currently enabled."""
    return autostart_path().exists()


def enable_autostart() -> bool:
    """Enable autostart by creating desktop entry. Returns success."""
    desktop_path = autostart_path()
    desktop_path.parent.mkdir(parents=True, exist_ok=True)

    start_script = get_start_script_path()
    content = DESKTOP_ENTRY.format(exec_path=start_script)

    try:
        desktop_path.write_text(content, encoding="utf-8")
        return True
    except OSError:
        return False


def disable_autostart() -> bool:
    """Disable autostart by removing desktop entry. Returns success."""
    desktop_path = autostart_path()
    if desktop_path.exists():
        try:
            desktop_path.unlink()
            return True
        except OSError:
            return False
    return True  # Already disabled
