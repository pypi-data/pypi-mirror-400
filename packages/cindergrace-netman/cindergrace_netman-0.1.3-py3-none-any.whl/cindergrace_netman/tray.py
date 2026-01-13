import threading
import time
import webbrowser

import pystray
from PIL import Image, ImageDraw

from .net import NetmanError, apply_limit, clear_limit, get_default_interface
from .state import load_state, save_state


def _make_icon(enabled: bool) -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color = (10, 107, 95, 255) if enabled else (224, 140, 59, 255)
    draw.ellipse((10, 10, size - 10, size - 10), fill=color)
    return img


def _tooltip(state: dict, iface: str | None) -> str:
    rate = state["base_mbit"] * state["percent"] / 100
    status = "aktiv" if state["enabled"] else "aus"
    iface_text = iface or "?"
    return f"Netman {status} | {state['percent']}% ({rate:.2f} Mbit/s) | {iface_text}"


def _toggle(icon: pystray.Icon, _item: pystray.MenuItem) -> None:
    state = load_state()
    iface = state["iface"] or get_default_interface()
    if not iface:
        return
    if state["enabled"]:
        try:
            clear_limit(iface)
        except NetmanError:
            return
        state["enabled"] = False
    else:
        rate = state["base_mbit"] * state["percent"] / 100
        try:
            apply_limit(iface, rate)
        except NetmanError:
            return
        state["enabled"] = True
    save_state(state)
    icon.icon = _make_icon(state["enabled"])
    icon.title = _tooltip(state, iface)


def _open_ui(_icon: pystray.Icon, _item: pystray.MenuItem) -> None:
    webbrowser.open("http://127.0.0.1:7863")  # Siehe gradio_ports.json


def run_tray() -> None:
    state = load_state()
    iface = state["iface"] or get_default_interface()
    icon = pystray.Icon(
        "cindergrace_netman",
        _make_icon(state["enabled"]),
        title=_tooltip(state, iface),
        menu=pystray.Menu(
            pystray.MenuItem("Toggle Limit", _toggle),
            pystray.MenuItem("Open UI", _open_ui),
            pystray.MenuItem("Quit", lambda icon, _item: icon.stop()),
        ),
    )

    def _watch_state() -> None:
        last_enabled = state["enabled"]
        last_percent = state["percent"]
        last_base = state["base_mbit"]
        last_iface = iface
        while True:
            time.sleep(2)
            current = load_state()
            current_iface = current["iface"] or get_default_interface()
            if (
                current["enabled"] != last_enabled
                or current["percent"] != last_percent
                or current["base_mbit"] != last_base
                or current_iface != last_iface
            ):
                icon.icon = _make_icon(current["enabled"])
                icon.title = _tooltip(current, current_iface)
                last_enabled = current["enabled"]
                last_percent = current["percent"]
                last_base = current["base_mbit"]
                last_iface = current_iface

    watcher = threading.Thread(target=_watch_state, daemon=True)
    watcher.start()
    icon.run()
