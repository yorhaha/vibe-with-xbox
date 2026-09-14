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
    "RIGHT_STICK_X": 2,
    "RIGHT_STICK_Y": 3,
    "RT": 5,
}

CONTROL_NAMES = {
    "A": "A",
    "B": "B",
    "X": "X",
    "Y": "Y",
    "START": "Start 键",
    "LB": "LB",
    "RB": "RB",
    "DPAD_UP": "十字键上",
    "DPAD_DOWN": "十字键下",
    "DPAD_LEFT": "十字键左",
    "DPAD_RIGHT": "十字键右",
    "LEFT_STICK_UP": "左摇杆上",
    "LEFT_STICK_DOWN": "左摇杆下",
    "RIGHT_STICK_UP": "右摇杆上",
    "RIGHT_STICK_DOWN": "右摇杆下",
    "RIGHT_STICK_LEFT": "右摇杆左",
    "RIGHT_STICK_RIGHT": "右摇杆右",
    "RT": "RT",
}

GUIDE_ORDER = [
    "A",
    "B",
    "X",
    "Y",
    "LEFT_STICK_UP",
    "LEFT_STICK_DOWN",
    "RIGHT_STICK_UP",
    "RIGHT_STICK_DOWN",
    "RIGHT_STICK_LEFT",
    "RIGHT_STICK_RIGHT",
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
    "version": 9,
    "general": {
        "auto_start_bridge": False,
        "deadzone": 0.5,
        "trigger_threshold": 0.2,
        "repeat_initial_delay": 0.35,
        "repeat_rate": 0.08,
        "show_action_toasts": True,
    },
    "buttons": {
        "A": {
            "enabled": True,
            "label": "Enter",
            "description": "确认当前提示或提交当前选择。",
            "action": "key",
            "key": "return",
        },
        "B": {
            "enabled": True,
            "label": "Esc",
            "description": "取消操作、关闭选择器或返回。",
            "action": "key",
            "key": "escape",
        },
        "X": {
            "enabled": True,
            "label": "按住右 Option",
            "description": "按住 X 时保持按下 macOS 右 Option 键。",
            "action": "hold_key",
            "key": "right_option",
        },
        "Y": {
            "enabled": True,
            "label": "↓ + Enter",
            "description": "下移一项并确认，适用于确认或自动编辑提示。",
            "action": "sequence",
            "keys": ["down", "return"],
        },
        "START": {
            "enabled": True,
            "label": "粘贴重启指令",
            "description": "输入：在本分支commit & push代码，然后温和重启项目",
            "action": "text",
            "text": "在本分支commit & push代码，然后温和重启项目",
        },
        "LB": {
            "enabled": True,
            "label": "上一个会话",
            "description": "切换到上一个 tmux session。",
            "action": "tmux",
            "command": "switch-client -p",
        },
        "RB": {
            "enabled": True,
            "label": "下一个会话",
            "description": "切换到下一个 tmux session。",
            "action": "tmux",
            "command": "switch-client -n",
        },
        "DPAD_UP": {
            "enabled": True,
            "label": "新建上方窗格",
            "description": "在当前 tmux 窗格上方新建窗格。",
            "action": "tmux",
            "command": "split-window -v -b",
        },
        "DPAD_DOWN": {
            "enabled": True,
            "label": "新建下方窗格",
            "description": "在当前 tmux 窗格下方新建窗格。",
            "action": "tmux",
            "command": "split-window -v",
        },
        "DPAD_LEFT": {
            "enabled": True,
            "label": "新建左侧窗格",
            "description": "在当前 tmux 窗格左侧新建窗格。",
            "action": "tmux",
            "command": "split-window -h -b",
        },
        "DPAD_RIGHT": {
            "enabled": True,
            "label": "新建右侧窗格",
            "description": "在当前 tmux 窗格右侧新建窗格。",
            "action": "tmux",
            "command": "split-window -h",
        },
    },
    "stick": {
        "LEFT_STICK_UP": {
            "enabled": True,
            "label": "上方向键",
            "description": "发送上方向键，持续拨动时自动重复。",
            "action": "key",
            "key": "up",
        },
        "LEFT_STICK_DOWN": {
            "enabled": True,
            "label": "下方向键",
            "description": "发送下方向键，持续拨动时自动重复。",
            "action": "key",
            "key": "down",
        },
        "RIGHT_STICK_UP": {
            "enabled": True,
            "label": "切换到上方窗格",
            "description": "在当前 tmux session 中切换到上方窗格。",
            "action": "tmux",
            "command": "select-pane -U",
        },
        "RIGHT_STICK_DOWN": {
            "enabled": True,
            "label": "切换到下方窗格",
            "description": "在当前 tmux session 中切换到下方窗格。",
            "action": "tmux",
            "command": "select-pane -D",
        },
        "RIGHT_STICK_LEFT": {
            "enabled": True,
            "label": "切换到左侧窗格",
            "description": "在当前 tmux session 中切换到左侧窗格。",
            "action": "tmux",
            "command": "select-pane -L",
        },
        "RIGHT_STICK_RIGHT": {
            "enabled": True,
            "label": "切换到右侧窗格",
            "description": "在当前 tmux session 中切换到右侧窗格。",
            "action": "tmux",
            "command": "select-pane -R",
        },
    },
    "triggers": {
        "RT": {
            "enabled": True,
            "label": "长按：关闭窗格",
            "description": "长按 RT，关闭当前 tmux 窗格。",
            "action": "tmux",
            "command": "kill-pane",
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
    version = int(user_config.get("version", 1))
    if version < 3:
        legacy_x = user_config.get("buttons", {}).get("X", {})
        if legacy_x.get("action") == "dictation":
            user_config["buttons"]["X"] = copy.deepcopy(DEFAULT_CONFIG["buttons"]["X"])
        user_config.pop("macos", None)
    if version < 5:
        legacy_x = user_config.get("buttons", {}).get("X", {})
        if legacy_x.get("action") == "hold_key" and legacy_x.get("key") == "option":
            user_config["buttons"]["X"] = copy.deepcopy(DEFAULT_CONFIG["buttons"]["X"])
    if version < 6:
        buttons = user_config.get("buttons", {})
        old_lb = buttons.get("LB", {})
        if old_lb.get("action") == "tmux_keys" and old_lb.get("command") == "select-pane -t :.-":
            buttons["LB"] = copy.deepcopy(DEFAULT_CONFIG["buttons"]["LB"])
        old_rb = buttons.get("RB", {})
        if old_rb.get("action") == "tmux_keys" and old_rb.get("command") == "select-pane -t :.+":
            buttons["RB"] = copy.deepcopy(DEFAULT_CONFIG["buttons"]["RB"])
    if version < 8:
        user_config.get("general", {}).pop("start_hold_seconds", None)
        buttons = user_config.get("buttons", {})
        old_start = buttons.get("START", {})
        if old_start.get("action") == "toggle_mapping":
            buttons["START"] = copy.deepcopy(DEFAULT_CONFIG["buttons"]["START"])
    if version < 9:
        user_config.pop("tmux", None)
        for section in ("buttons", "stick", "triggers"):
            for mapping in user_config.get(section, {}).values():
                if mapping.get("action") == "tmux_keys":
                    mapping["action"] = "tmux"
    user_config["version"] = 9
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
    return {
        "enabled": False,
        "label": "未映射",
        "description": "尚未分配操作。",
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
                "label": str(mapping.get("label", "未映射")),
                "description": str(mapping.get("description", "")),
            }
        )
    return rows
