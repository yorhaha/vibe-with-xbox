from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .bridge import BridgeEvent, ControllerBridge
from .config import CONFIG_PATH, guide_rows, load_config, write_default_config
from .doctor import run_checks
from .ui import run_gui


def print_event(event: BridgeEvent) -> None:
    if event.kind == "debug":
        print(event.message)
    elif event.kind == "action":
        print(f"{event.control}: {event.action_label}")
    elif event.message:
        print(event.message)


def run_headless(config: dict, debug: bool = False) -> int:
    bridge = ControllerBridge(config, callback=print_event, debug=debug, send_actions=not debug)
    try:
        return bridge.run()
    except KeyboardInterrupt:
        bridge.stop()
        print()
        return 0


def print_mapping(config: dict) -> None:
    for row in guide_rows(config):
        print(f"{row['name']:<17} {row['label']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Xbox controller bridge for Claude Code and tmux."
    )
    parser.add_argument("--config", type=Path, help="path to a custom config.json")
    parser.add_argument("--headless", action="store_true", help="run without the desktop guide")
    parser.add_argument("--debug", action="store_true", help="print raw controller events")
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="check controller, Accessibility permission, and tmux",
    )
    parser.add_argument("--init-config", action="store_true", help="write the default config file")
    parser.add_argument("--print-config-path", action="store_true", help="print the user config path")
    parser.add_argument("--show-mapping", action="store_true", help="print the current mapping")
    args = parser.parse_args(argv)

    config_path = args.config

    if args.print_config_path:
        print(config_path or CONFIG_PATH)
        return 0

    if args.init_config:
        path = write_default_config(config_path)
        print(path)
        return 0

    config = load_config(config_path)

    if args.doctor:
        for check in run_checks():
            print(f"{check.name:<15} {check.status.upper():<5} {check.message}")
        return 0

    if args.show_mapping:
        print_mapping(config)
        return 0

    if args.headless or args.debug:
        return run_headless(config, debug=args.debug)

    return run_gui(config_path)


if __name__ == "__main__":
    sys.exit(main())
