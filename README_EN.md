# Vibe with Xbox

[简体中文](README.md) | **English**

Turn an Xbox controller into a lightweight macOS remote for **Claude Code** and **tmux**.

Vibe with Xbox opens a local controller guide and status page in your browser. Once the controller is connected and the mapping is running, you can confirm or cancel Claude Code prompts, move through choices, hold the right Option modifier, and manage tmux panes from the controller.

> Current version: `0.2.0`. macOS only.

## Features

- Shows the controller, active mapping, connection status, and latest action in a browser, highlighting controls in real time when physical buttons are pressed.
- The page can run the setup checks, open the config file, jump to the Accessibility settings, and quit the app.
- Sends `Enter`, `Esc`, arrow keys, and the right `Option` modifier to the focused macOS app.
- Manages local tmux panes and sessions with the D-pad, right stick, LB, RB, and RT, invoking the local `tmux` CLI directly without depending on foreground-window focus.
- Pressing Start types the configured commit, push, and graceful-restart instruction into the focused app.
- Includes setup checks, raw controller event debugging, custom JSON configuration, and a headless mode.
- The local guide listens only on `127.0.0.1`; the project does not send controller events to the cloud.

## Default Mapping

| Controller input | Default action |
| --- | --- |
| A | `Enter` |
| B | `Esc` |
| Hold X | Hold the right `Option` key |
| Y | `↓` + `Enter` |
| Left stick up / down | `↑` / `↓` (auto-repeats while held) |
| Right stick up / down / left / right | Switch to the tmux pane in that direction |
| D-pad up / down / left / right | Create a tmux pane in that direction |
| LB / RB | Previous / next tmux session |
| Hold RT for 0.7s | Close the current tmux pane |
| Start | Type the restart instruction (does not press Enter) |

LT, stick clicks, View, Share, the Xbox button, and left-stick left/right are not mapped yet. See [Controller Mapping](docs/controller-mapping.md) for per-button details (Chinese).

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python xbox_vibe.py --doctor   # environment check
python xbox_vibe.py            # run
```

Before starting, connect the controller in **System Settings → Bluetooth** and grant **System Settings → Privacy & Security → Accessibility** permission to Terminal or Python. tmux pane controls additionally require tmux installed locally and a running tmux session in your terminal.

The app opens `http://127.0.0.1:8765/` in your default browser, falling back to another local port if that one is taken. The page runs the setup checks automatically on load; once the controller check looks good, click **启动手柄映射** (start mapping), then switch to your target app and keep it focused. When you are done, click **停止** (stop) to stop the mapping or **退出应用** (quit) to exit the app. The page interface is in Chinese.

> The mapping sends system-level keystrokes, so actions apply to whichever app currently has focus. Make sure the right window is focused before you start.

Full setup steps: [Installation](docs/installation.md) (Chinese).

## Documentation

The detailed documentation is currently available in Chinese only.

| Document | Contents |
| --- | --- |
| [Installation](docs/installation.md) | Requirements, dependencies, Bluetooth and Accessibility setup |
| [Usage](docs/usage.md) | Startup flow, page controls, headless mode, CLI flags |
| [Controller Mapping](docs/controller-mapping.md) | Full mapping table and per-button behaviour |
| [Configuration](docs/configuration.md) | Config file location, merge rules, tunable options |
| [Troubleshooting](docs/troubleshooting.md) | Controller, keys, right Option, tmux, and page issues |
| [Build the macOS App](docs/build-macos-app.md) | PyInstaller packaging and signing |
| [Development](docs/development.md) | Project layout, tests, contributing |

## License

Released under the [MIT License](LICENSE).
