from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

APP_NAME = "Vibe with Xbox"
APP_ID = "vibe-with-xbox"

CONFIG_DIR = Path.home() / ".config" / APP_ID
CONFIG_PATH = CONFIG_DIR / "config.json"

BUTTON_INDEXES = {
    "A": 0,
    "B": 1,
    "X": 2,
    "Y": 3,
    "START": 6,
    "LB": 9,
    "RB": 10,
    "DPAD_UP": 11,
    "DPAD_DOWN": 12,
    "DPAD_LEFT": 13,
    "DPAD_RIGHT": 14,
}

AXIS_INDEXES = {
    "LEFT_STICK_Y": 1,
    "RT": 5,
}

CONTROL_NAMES = {
    "A": "A",
    "B": "B",
    "X": "X",
    "Y": "Y",
    "START": "Start",
    "LB": "LB",
    "RB": "RB",
    "DPAD_UP": "D-pad Up",
    "DPAD_DOWN": "D-pad Down",
    "DPAD_LEFT": "D-pad Left",
    "DPAD_RIGHT": "D-pad Right",
    "LEFT_STICK_UP": "Left Stick Up",
    "LEFT_STICK_DOWN": "Left Stick Down",
    "RT": "RT",
}

GUIDE_ORDER = [
    "A",
    "B",
    "X",
    "Y",
    "LEFT_STICK_UP",
    "LEFT_STICK_DOWN",
    "DPAD_UP",
    "DPAD_DOWN",
    "DPAD_LEFT",
    "DPAD_RIGHT",
    "LB",
    "RB",
    "RT",
    "START",
]

DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "general": {
        "auto_start_bridge": False,
        "deadzone": 0.5,
        "trigger_threshold": 0.2,
        "repeat_initial_delay": 0.35,
        "repeat_rate": 0.08,
        "start_hold_seconds": 1.0,
        "show_action_toasts": True,
    },
    "macos": {
        "dictation_key": "f5",
        "dictation_flags": 0,
    },
    "buttons": {
        "A": {
            "enabled": True,
            "label": "Enter",
            "description": "Confirm the current prompt or send the current choice.",
            "action": "key",
            "key": "return",
        },
        "B": {
            "enabled": True,
            "label": "Esc",
            "description": "Cancel, close a picker, or back out of the current UI.",
            "action": "key",
            "key": "escape",
        },
        "X": {
            "enabled": True,
            "label": "Dictation",
            "description": "Toggle macOS Dictation using the configured shortcut.",
            "action": "dictation",
        },
        "Y": {
            "enabled": True,
            "label": "Down + Enter",
            "description": "Select the next option, useful for yes / auto-edit prompts.",
            "action": "sequence",
            "keys": ["down", "return"],
        },
        "LB": {
            "enabled": True,
            "label": "Previous pane",
            "description": "Move focus to the previous tmux pane.",
            "action": "tmux",
            "args": ["select-pane", "-t", ":.-"],
        },
        "RB": {
            "enabled": True,
            "label": "Next pane",
            "description": "Move focus to the next tmux pane.",
            "action": "tmux",
            "args": ["select-pane", "-t", ":.+"],
        },
        "DPAD_UP": {
            "enabled": True,
            "label": "New pane above",
            "description": "Split the active tmux pane and create a pane above it.",
            "action": "tmux",
            "args": ["split-window", "-v", "-b"],
        },
        "DPAD_DOWN": {
            "enabled": True,
            "label": "New pane below",
            "description": "Split the active tmux pane and create a pane below it.",
            "action": "tmux",
            "args": ["split-window", "-v"],
        },
        "DPAD_LEFT": {
            "enabled": True,
            "label": "New pane left",
            "description": "Split the active tmux pane and create a pane on the left.",
            "action": "tmux",
            "args": ["split-window", "-h", "-b"],
        },
        "DPAD_RIGHT": {
            "enabled": True,
            "label": "New pane right",
            "description": "Split the active tmux pane and create a pane on the right.",
            "action": "tmux",
            "args": ["split-window", "-h"],
        },
    },
    "stick": {
        "LEFT_STICK_UP": {
            "enabled": True,
            "label": "Up",
            "description": "Send Up arrow with auto-repeat while held.",
            "action": "key",
            "key": "up",
        },
        "LEFT_STICK_DOWN": {
            "enabled": True,
            "label": "Down",
            "description": "Send Down arrow with auto-repeat while held.",
            "action": "key",
            "key": "down",
        },
    },
    "triggers": {
        "RT": {
            "enabled": True,
            "label": "Hold: close pane",
            "description": "Hold RT to destroy the current tmux pane.",
            "action": "tmux",
            "args": ["kill-pane"],
            "hold_seconds": 0.7,
        },
    },
}


def deep_merge(default: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(default)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: Path | None = None) -> dict[str, Any]:
    config_path = path or CONFIG_PATH
    if not config_path.exists():
        return copy.deepcopy(DEFAULT_CONFIG)
    with config_path.open("r", encoding="utf-8") as f:
        user_config = json.load(f)
    return deep_merge(DEFAULT_CONFIG, user_config)


def write_default_config(path: Path | None = None, overwrite: bool = False) -> Path:
    config_path = path or CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists() and not overwrite:
        return config_path
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
        f.write("\n")
    return config_path


def mapping_for_control(config: dict[str, Any], control: str) -> dict[str, Any]:
    if control in config.get("buttons", {}):
        return config["buttons"][control]
    if control in config.get("stick", {}):
        return config["stick"][control]
    if control in config.get("triggers", {}):
        return config["triggers"][control]
    if control == "START":
        hold = config.get("general", {}).get("start_hold_seconds", 1.0)
        return {
            "enabled": True,
            "label": f"Hold {hold:g}s: pause",
            "description": "Toggle the whole controller mapping on or off.",
            "action": "toggle_mapping",
        }
    return {
        "enabled": False,
        "label": "Unmapped",
        "description": "No action is assigned.",
        "action": "none",
    }


def guide_rows(config: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for control in GUIDE_ORDER:
        mapping = mapping_for_control(config, control)
        rows.append(
            {
                "control": control,
                "name": CONTROL_NAMES.get(control, control),
                "label": str(mapping.get("label", "Unmapped")),
                "description": str(mapping.get("description", "")),
            }
        )
    return rows
