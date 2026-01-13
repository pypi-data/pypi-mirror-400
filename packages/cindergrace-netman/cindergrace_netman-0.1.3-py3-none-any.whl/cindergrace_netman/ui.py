"""NetMan Gradio UI with i18n support."""

from __future__ import annotations

from pathlib import Path

import gradio as gr
from gradio_i18n import Translate
from gradio_i18n import gettext as _

from .checks import download_test, ping
from .net import (
    NetmanError,
    apply_limit,
    clear_limit,
    get_default_interface,
    list_interfaces_with_info,
)
from .state import (
    disable_autostart,
    enable_autostart,
    is_autostart_enabled,
    load_state,
    save_state,
)

# Translation file
TRANSLATIONS = Path(__file__).parent / "translations" / "ui.yaml"

# Cindergrace Unified Theme - LIGHT
CSS = """
@import url("https://fonts.googleapis.com/css2?family=Comfortaa:wght@400;600;700&family=Nunito:wght@400;500;600&display=swap");

:root {
    --cg-blue-dark: #1E5AA8;
    --cg-blue-light: #7CC8FF;
    --cg-blue-hover: #2d6fc0;
    --cg-bg-primary: #f8f9fc;
    --cg-bg-secondary: #ffffff;
    --cg-bg-card: #ffffff;
    --cg-bg-input: #f4f6f8;
    --cg-text-primary: #1c2321;
    --cg-text-secondary: #4a5568;
    --cg-text-muted: #718096;
    --cg-success: #2ecc71;
    --cg-warning: #f39c12;
    --cg-error: #e74c3c;
    --cg-font-size-base: 17px;
    --cg-font-size-label: 16px;
    --cg-border-radius: 12px;
    --cg-max-width: 1000px;
    --cg-spacing: 20px;
}

body, .gradio-container {
    background: linear-gradient(135deg, var(--cg-bg-primary) 0%, #eef1f5 100%) !important;
    color: var(--cg-text-primary) !important;
    font-family: "Nunito", "Segoe UI", system-ui, sans-serif !important;
    font-size: var(--cg-font-size-base) !important;
}

.gradio-container {
    max-width: var(--cg-max-width) !important;
    margin: 0 auto !important;
    padding: var(--cg-spacing) !important;
}

.logo-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 8px;
}

.logo-header svg { width: 48px; height: 48px; }

h1, h2, h3, .markdown-text h1, .markdown-text h2, .markdown-text h3 {
    font-family: "Comfortaa", sans-serif !important;
    color: var(--cg-blue-dark) !important;
    font-weight: 600 !important;
}

h1, .markdown-text h1 { font-size: 2em !important; }
h2, .markdown-text h2 {
    font-size: 1.4em !important;
    border-bottom: 2px solid var(--cg-blue-light);
    padding-bottom: 0.3em;
    margin-top: 1em !important;
}

.panel, .gr-group, .gr-box, .block {
    background: var(--cg-bg-card) !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: var(--cg-border-radius) !important;
    padding: var(--cg-spacing) !important;
    box-shadow: 0 4px 16px rgba(30, 90, 168, 0.08) !important;
    margin-bottom: var(--cg-spacing) !important;
}

label, .gr-input-label, .label-wrap, .label-wrap span,
.gr-box label, .gr-form label, span.svelte-1gfkn6j,
.wrap label, .block label, .container label {
    color: var(--cg-text-secondary) !important;
    font-size: var(--cg-font-size-label) !important;
    font-weight: 600 !important;
    margin-bottom: 6px !important;
}

input, textarea, select, .gr-input, .gr-textbox textarea,
input[type="text"], input[type="number"] {
    background: var(--cg-bg-input) !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    color: var(--cg-text-primary) !important;
    font-size: var(--cg-font-size-base) !important;
    padding: 10px 14px !important;
}

input:focus, textarea:focus, select:focus {
    border-color: var(--cg-blue-dark) !important;
    box-shadow: 0 0 0 3px rgba(30, 90, 168, 0.15) !important;
    outline: none !important;
}

button, .gr-button {
    font-family: "Nunito", sans-serif !important;
    font-size: var(--cg-font-size-base) !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
}

button.primary, .gr-button.primary, button[variant="primary"] {
    background: linear-gradient(135deg, var(--cg-blue-dark) 0%, var(--cg-blue-hover) 100%) !important;
    color: white !important;
    border: none !important;
}

button.primary:hover, .gr-button.primary:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(30, 90, 168, 0.3) !important;
}

button.secondary, .gr-button.secondary {
    background: white !important;
    color: var(--cg-blue-dark) !important;
    border: 2px solid var(--cg-blue-dark) !important;
}

button.secondary:hover { background: var(--cg-bg-input) !important; }

.markdown-text, .prose {
    font-size: var(--cg-font-size-base) !important;
    color: var(--cg-text-primary) !important;
}

.markdown-text code, .prose code {
    background: #e8f4fd !important;
    color: var(--cg-blue-dark) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.95em !important;
}

.gr-slider input[type="range"], input[type="range"] {
    accent-color: var(--cg-blue-dark) !important;
}

input[type="checkbox"] {
    accent-color: var(--cg-blue-dark) !important;
    width: 18px !important;
    height: 18px !important;
}

.app-header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;
}

.app-header svg {
    width: 48px;
    height: 48px;
    flex-shrink: 0;
}

.app-header h1 {
    margin: 0 !important;
    font-size: 1.8em !important;
}

.app-header .subtitle {
    color: var(--cg-text-muted);
    font-size: 0.95em;
    margin-top: 2px;
}
"""

LOGO_SVG = """<svg width="48" height="48" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="512" height="512" rx="96" fill="white"/>
  <circle cx="256" cy="256" r="200" stroke="#7CC8FF" stroke-width="36" fill="none"/>
  <path d="M 56 256 L 56 490" stroke="#7CC8FF" stroke-width="36" stroke-linecap="round"/>
  <path d="M 420 256 A 164 164 0 1 1 338 114" stroke="#1E5AA8" stroke-width="36" stroke-linecap="round"/>
  <path d="M 420 256 L 320 256" stroke="#1E5AA8" stroke-width="36" stroke-linecap="round"/>
  <path d="M 332 180 A 108 108 0 1 0 332 332" stroke="#7CC8FF" stroke-width="28" stroke-linecap="round"/>
</svg>"""


def _get_interface_choices() -> list[tuple[str, str]]:
    """Build interface dropdown with speed and status info."""
    interfaces = list_interfaces_with_info()
    choices = []
    for iface in interfaces:
        name = iface["name"]
        speed = iface["speed_mbit"]
        state = iface["state"]
        is_default = iface["is_default"]

        label_parts = [name]
        if speed:
            label_parts.append(f"{speed} Mbit/s")
        if state == "up":
            label_parts.append("✓")
        elif state == "down":
            label_parts.append("✗")
        if is_default:
            label_parts.append("⬤")

        label = " | ".join(label_parts)
        choices.append((label, name))

    return choices


def _apply_saved_limit() -> None:
    """Apply saved limit on startup if enabled in state."""
    state = load_state()
    if not state.get("enabled"):
        return

    iface = state["iface"] or get_default_interface()
    if not iface:
        return

    base = state["base_mbit"]
    percent = state["percent"]
    rate = base * percent / 100

    try:
        apply_limit(iface, rate)
    except NetmanError:
        # Silently fail on startup - user will see status
        pass


def _format_status(lang: str) -> str:
    """Format current status as markdown string (called dynamically)."""
    state = load_state()
    iface = state["iface"] or get_default_interface() or "?"
    base = state["base_mbit"]

    default_iface = get_default_interface()
    route_marker = f"⬤ {_('default_route')}" if iface == default_iface else ""

    if state["enabled"]:
        percent = state["percent"]
        rate = base * percent / 100
        status_text = f"🔴 **{_('limit')} {_('status_active')}:** {percent}% = {rate:.2f} Mbit/s"
    else:
        status_text = f"🟢 {_('no_limit')}"

    return (
        f"**{_('status')}:** {status_text}  |  "
        f"**{_('interface')}:** `{iface}` {route_marker}  |  "
        f"**{_('dsl')}:** {base} Mbit/s"
    )


def _apply_settings(
    enable: bool,
    percent: int,
    base_mbit: int,
    iface: str,
    download_url: str,
    ping_host_val: str,
    lang: str,
) -> str:
    """Apply network limit settings."""
    if not iface:
        return _("no_interface")
    state = load_state()
    state["percent"] = int(percent)
    state["base_mbit"] = int(base_mbit)
    state["iface"] = iface
    state["download_url"] = download_url
    state["ping_host"] = ping_host_val

    if enable:
        rate = base_mbit * percent / 100
        try:
            apply_limit(iface, rate)
        except NetmanError as exc:
            return f"{_('error_enable')}: {exc}"
        state["enabled"] = True
        save_state(state)
        return f"{_('limit_active_msg')}: {percent}% ({rate:.2f} Mbit/s) @ `{iface}`"

    try:
        clear_limit(iface)
    except NetmanError as exc:
        return f"{_('error_disable')}: {exc}"
    state["enabled"] = False
    save_state(state)
    return _("limit_disabled")


def _refresh_status(lang: str) -> tuple[str, gr.Dropdown]:
    """Refresh UI state from saved settings."""
    state = load_state()
    choices = _get_interface_choices()
    interface_names = [c[1] for c in choices]
    default_iface = (
        state["iface"] or get_default_interface() or (interface_names[0] if interface_names else "")
    )
    status = _format_status(lang)
    return status, gr.Dropdown(choices=choices, value=default_iface)


def _run_ping(host: str, count: int, interval: float, lang: str) -> str:
    """Run ping test and return results."""
    try:
        result = ping(host, count=count, interval=interval)
    except NetmanError as exc:
        return f"{_('ping_failed')}: {exc}"
    return (
        f"**{_('ping_result')} {host}**\n\n"
        f"- {_('transmitted')}: {result['transmitted']}\n"
        f"- {_('received')}: {result['received']}\n"
        f"- {_('packet_loss')}: {result['loss_percent']}%\n"
        f"- {_('min_avg_max_jitter')}: {result['min_ms']} / {result['avg_ms']} / "
        f"{result['max_ms']} / {result['mdev_ms']} ms"
    )


def _run_download(url: str, max_mb: int, lang: str) -> str:
    """Run download speed test and return results."""
    try:
        result = download_test(url, max_mb=max_mb)
    except NetmanError as exc:
        return f"{_('download_failed')}: {exc}"
    return (
        f"**{_('download_result')}**\n\n"
        f"- {_('data')}: {result['bytes_read'] / (1024 * 1024):.2f} MB\n"
        f"- {_('time')}: {result['elapsed_s']:.2f} s\n"
        f"- {_('rate')}: {result['mbit_per_s']:.2f} Mbit/s"
    )


def _save_language(new_lang: str) -> None:
    """Save language preference to config."""
    state = load_state()
    state["language"] = new_lang
    save_state(state)


def _save_settings(dsl_speed: int, ping_host_val: str, download_url_val: str, new_lang: str) -> str:
    """Save all settings to config."""
    state = load_state()
    state["base_mbit"] = int(dsl_speed)
    state["ping_host"] = ping_host_val
    state["download_url"] = download_url_val
    state["language"] = new_lang
    save_state(state)
    return _("settings_saved")


def _toggle_limit(
    percent_val: int,
    iface_val: str,
    dsl_val: int,
    lang_val: str,
) -> tuple[str, gr.Button]:
    """Toggle network limit on/off."""
    state = load_state()
    state["percent"] = int(percent_val)
    state["iface"] = iface_val
    currently_enabled = state["enabled"]

    if currently_enabled:
        # Disable limit
        try:
            clear_limit(iface_val)
        except NetmanError:
            pass  # Ignore errors when disabling
        state["enabled"] = False
        save_state(state)
        new_btn = gr.Button(value=_("enable_limit"), variant="primary")
    else:
        # Enable limit
        rate = dsl_val * percent_val / 100
        try:
            apply_limit(iface_val, rate)
        except NetmanError:
            # Return error but keep button state
            status = _format_status(lang_val)
            return status, gr.Button(value=_("enable_limit"), variant="primary")
        state["enabled"] = True
        save_state(state)
        new_btn = gr.Button(value=_("disable_limit"), variant="stop")

    status = _format_status(lang_val)
    return status, new_btn


def _toggle_autostart() -> tuple[str, gr.Button]:
    """Toggle autostart on/off."""
    currently_enabled = is_autostart_enabled()
    if currently_enabled:
        success = disable_autostart()
        if success:
            state = load_state()
            state["autostart"] = False
            save_state(state)
            return (
                _("autostart_disabled"),
                gr.Button(value=_("autostart_disabled"), variant="primary"),
            )
        return (
            _("autostart_error"),
            gr.Button(value=_("autostart_enabled"), variant="stop"),
        )
    else:
        success = enable_autostart()
        if success:
            state = load_state()
            state["autostart"] = True
            save_state(state)
            return (
                _("autostart_enabled"),
                gr.Button(value=_("autostart_enabled"), variant="stop"),
            )
        return (
            _("autostart_error"),
            gr.Button(value=_("autostart_disabled"), variant="primary"),
        )


def _save_and_update(
    dsl: int, ping_host_val: str, dl_url: str, new_lang: str
) -> tuple[str, int, str, str, str]:
    """Save settings and return updated values for state."""
    msg = _save_settings(dsl, ping_host_val, dl_url, new_lang)
    return msg, dsl, ping_host_val, dl_url, new_lang


def _get_default_interface_value(state: dict, interface_names: list[str]) -> str:
    """Get default interface from state or system."""
    stored = state.get("iface")
    if stored:
        return stored
    default = get_default_interface()
    if default:
        return default
    return interface_names[0] if interface_names else ""


def _get_toggle_button_props(enabled: bool) -> tuple[str, str]:
    """Get label and variant for toggle button based on limit state."""
    if enabled:
        return _("disable_limit"), "stop"
    return _("enable_limit"), "primary"


def _get_autostart_button_props(enabled: bool) -> tuple[str, str]:
    """Get label and variant for autostart button."""
    if enabled:
        return _("autostart_enabled"), "stop"
    return _("autostart_disabled"), "primary"


def _get_tab_labels(lang: str) -> tuple[str, str]:
    """Get localized tab labels."""
    if lang == "de":
        return "Netzwerk", "Einstellungen"
    return "Network", "Settings"


def build_app() -> gr.Blocks:
    """Build the Gradio application with i18n support and tabs."""
    _apply_saved_limit()

    state = load_state()
    choices = _get_interface_choices()
    interface_names = [c[1] for c in choices]
    default_iface = _get_default_interface_value(state, interface_names)
    saved_lang = state.get("language", "en")
    tab_network_label, tab_settings_label = _get_tab_labels(saved_lang)

    with gr.Blocks(css=CSS, title="CinderGrace Projects - NetMan") as app:
        with Translate(
            str(TRANSLATIONS),
            placeholder_langs=["en", "de"],
        ) as lang:
            lang.value = saved_lang

            gr.HTML(f"""
            <div class="app-header">
                {LOGO_SVG}
                <div>
                    <h1 style="margin:0 !important; font-size:1.8em !important;">CinderGrace Projects - NetMan</h1>
                </div>
            </div>
            """)

            with gr.Tabs():
                with gr.TabItem(tab_network_label):
                    with gr.Group(elem_classes=["panel"]):
                        status_md = gr.Markdown()
                        with gr.Row():
                            iface_dropdown = gr.Dropdown(
                                choices=choices,
                                value=default_iface,
                                label=_("interface"),
                                interactive=True,
                            )
                            percent = gr.Slider(
                                minimum=1,
                                maximum=100,
                                step=1,
                                value=state["percent"],
                                label=_("limit_percent"),
                            )
                        with gr.Row():
                            toggle_label, toggle_variant = _get_toggle_button_props(
                                state["enabled"]
                            )
                            toggle_btn = gr.Button(toggle_label, variant=toggle_variant)
                            refresh_btn = gr.Button(_("refresh"))

                    with gr.Group(elem_classes=["panel"]):
                        gr.Markdown(lambda: f"## {_('check_connection')}")
                        with gr.Row():
                            ping_count = gr.Slider(1, 20, value=6, step=1, label=_("packets"))
                            ping_interval = gr.Slider(
                                0.2, 1.0, value=0.3, step=0.1, label=_("interval_s")
                            )
                            ping_btn = gr.Button(_("start_ping"))
                        ping_out = gr.Markdown()

                        with gr.Row():
                            dl_size = gr.Slider(1, 100, value=10, step=1, label=_("max_mb"))
                            dl_btn = gr.Button(_("download_test"))
                        dl_out = gr.Markdown()

                # === TAB 2: Settings ===
                with gr.TabItem(tab_settings_label):
                    with gr.Group(elem_classes=["panel"]):
                        gr.Markdown(f"## {_('settings')}")
                        lang_dropdown = gr.Dropdown(
                            choices=[("English", "en"), ("Deutsch", "de")],
                            value=saved_lang,
                            label=_("language"),
                            interactive=True,
                        )
                        settings_dsl = gr.Number(
                            value=state["base_mbit"],
                            precision=0,
                            label=_("dsl_speed"),
                        )
                        settings_ping_host = gr.Textbox(
                            value=state.get("ping_host", "8.8.8.8"),
                            label=_("default_ping_host"),
                        )
                        settings_download_url = gr.Textbox(
                            value=state.get(
                                "download_url", "https://ash-speed.hetzner.com/100MB.bin"
                            ),
                            label=_("default_download_url"),
                        )
                        autostart_label, autostart_variant = _get_autostart_button_props(
                            is_autostart_enabled()
                        )
                        with gr.Row():
                            gr.Markdown(f"**{_('autostart')}:** {_('autostart_desc')}")
                        autostart_btn = gr.Button(autostart_label, variant=autostart_variant)
                        autostart_out = gr.Markdown()

                        save_settings_btn = gr.Button(_("save_settings"), variant="primary")
                        settings_out = gr.Markdown()

            # Hidden state for settings values (used by network tab)
            current_dsl = gr.State(value=state["base_mbit"])
            current_ping_host = gr.State(value=state.get("ping_host", "8.8.8.8"))
            current_download_url = gr.State(
                value=state.get("download_url", "https://ash-speed.hetzner.com/100MB.bin")
            )

            # Initialize dynamic status on page load
            app.load(
                _format_status,
                inputs=[lang],
                outputs=[status_md],
            )

            # === Event handlers (using module-level functions) ===

            toggle_btn.click(
                _toggle_limit,
                inputs=[percent, iface_dropdown, current_dsl, lang],
                outputs=[status_md, toggle_btn],
            )

            refresh_btn.click(
                _refresh_status,
                inputs=[lang],
                outputs=[status_md, iface_dropdown],
            )

            ping_btn.click(
                lambda c, i, h, lang: _run_ping(h, c, i, lang),
                inputs=[ping_count, ping_interval, current_ping_host, lang],
                outputs=ping_out,
            )

            dl_btn.click(
                lambda s, u, lang: _run_download(u, s, lang),
                inputs=[dl_size, current_download_url, lang],
                outputs=dl_out,
            )

            save_settings_btn.click(
                _save_and_update,
                inputs=[
                    settings_dsl,
                    settings_ping_host,
                    settings_download_url,
                    lang_dropdown,
                ],
                outputs=[
                    settings_out,
                    current_dsl,
                    current_ping_host,
                    current_download_url,
                    lang,
                ],
            )

            lang_dropdown.change(
                lambda x: x,
                inputs=[lang_dropdown],
                outputs=[lang],
            )

            autostart_btn.click(
                _toggle_autostart,
                inputs=[],
                outputs=[autostart_out, autostart_btn],
            )

    return app
