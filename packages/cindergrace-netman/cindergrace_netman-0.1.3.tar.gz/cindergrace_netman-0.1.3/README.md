# cindergrace_netman

**Status:** Final


> **Note:** This repository is a hobby/experimental project. It is not a commercial offering (no contract work, no warranties, no support promises).

![Status](https://img.shields.io/badge/Status-Final-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-PolyForm%20NC-green)

Network bandwidth management tool for Linux. Limit your download speed to avoid saturating your connection when downloading large files (AI models, game updates, etc.) while sharing bandwidth with others.

## Screenshots

![NetMan UI - Main](docs/images/netman-01.png)

![NetMan UI - Tests](docs/images/netman-02.png)

## Features

- **Bandwidth Limiting**: Set download limits as percentage of your DSL/fiber speed
- **Web UI**: Modern Gradio-based interface with real-time status
- **Internationalization**: English and German UI (configurable)
- **Connection Tests**: Built-in ping and download speed tests
- **Autostart**: Optional automatic start on login with saved limit settings
- **System Tray**: Optional tray icon for quick access

## Installation

```bash
pip install cindergrace-netman
```

Or clone and install locally:

```bash
git clone https://github.com/goettemar/cindergrace_netman.git
cd cindergrace_netman
pip install -e .
```

## Usage

### Quick Start (Recommended)

```bash
# Start the web UI (will prompt for sudo password)
./start.sh
```

The UI opens at `http://localhost:7863`

### Command Line

```bash
# Start Gradio UI
cindergrace-netman ui

# Set download limit to 60% of a 100 Mbit connection
sudo cindergrace-netman limit --percent 60 --base-mbit 100

# Remove limit
sudo cindergrace-netman clear

# Start system tray icon
cindergrace-netman tray
```

> **Note:** Setting limits via `tc` requires root privileges. For download limits, an IFB device (`ifb0`) is created.

## Configuration

Settings are stored in `~/.config/cindergrace_netman/state.json`:

- **Language**: English (default) or German
- **DSL Speed**: Your connection speed in Mbit/s
- **Default Ping Host**: Host for connection tests
- **Default Download URL**: URL for speed tests
- **Autostart**: Start NetMan automatically on login

## How It Works

NetMan uses Linux Traffic Control (`tc`) with an Intermediate Functional Block (IFB) device to shape incoming traffic. This allows limiting download bandwidth without affecting upload speeds.

## Development

```bash
# Clone repository
git clone https://github.com/goettemar/cindergrace_netman.git
cd cindergrace_netman

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/
```

## Project Structure

```
src/cindergrace_netman/
├── cli.py           # CLI entry point (argparse)
├── net.py           # Linux TC (qdisc) for bandwidth limiting
├── checks.py        # Ping and download speed tests
├── ui.py            # Gradio Web UI with i18n
├── tray.py          # System tray icon
├── state.py         # XDG-compliant state persistence
└── translations/
    └── ui.yaml      # UI translations (en/de)
```

## License

This project is licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE).

---

Created 2026-01-03 | [goettemar](https://github.com/goettemar)



