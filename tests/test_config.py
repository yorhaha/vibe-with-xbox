from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vibe_with_xbox.config import DEFAULT_CONFIG, load_config


class ConfigMigrationTests(unittest.TestCase):
    def test_default_config_has_no_remote_tmux_settings(self) -> None:
        self.assertNotIn("tmux", DEFAULT_CONFIG)

    def test_legacy_dictation_mapping_is_replaced_with_option(self) -> None:
        legacy = {
            "version": 2,
            "macos": {"dictation_key": "f5", "dictation_flags": 0},
            "buttons": {"X": {"action": "dictation", "label": "Dictation"}},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(legacy), encoding="utf-8")

            config = load_config(path)

        self.assertEqual(config["version"], 9)
        self.assertNotIn("macos", config)
        self.assertEqual(
            config["buttons"]["X"],
            {
                "enabled": True,
                "label": "按住右 Option",
                "description": "按住 X 时保持按下 macOS 右 Option 键。",
                "action": "hold_key",
                "key": "right_option",
            },
        )

    def test_legacy_tmux_transport_settings_are_removed(self) -> None:
        legacy = {
            "version": 3,
            "tmux": {"prefix": [{"key": "b", "modifiers": ["control"]}]},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(legacy), encoding="utf-8")

            config = load_config(path)

        self.assertNotIn("tmux", config)

    def test_old_left_option_mapping_is_migrated_to_right_option(self) -> None:
        legacy = {
            "version": 4,
            "buttons": {
                "X": {
                    "enabled": True,
                    "label": "按住 Option",
                    "description": "按住 X 时保持按下 macOS Option 键。",
                    "action": "hold_key",
                    "key": "option",
                }
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(legacy), encoding="utf-8")

            config = load_config(path)

        self.assertEqual(config["buttons"]["X"]["key"], "right_option")

    def test_old_default_pane_navigation_is_migrated_to_session_navigation(self) -> None:
        legacy = {
            "version": 5,
            "buttons": {
                "LB": {
                    "enabled": True,
                    "label": "上一个窗格",
                    "action": "tmux_keys",
                    "command": "select-pane -t :.-",
                },
                "RB": {
                    "enabled": True,
                    "label": "下一个窗格",
                    "action": "tmux_keys",
                    "command": "select-pane -t :.+",
                },
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(legacy), encoding="utf-8")

            config = load_config(path)

        self.assertEqual(config["version"], 9)
        self.assertEqual(config["buttons"]["LB"]["command"], "switch-client -p")
        self.assertEqual(config["buttons"]["RB"]["command"], "switch-client -n")
        self.assertEqual(config["buttons"]["LB"]["action"], "tmux")

    def test_custom_lb_rb_tmux_commands_are_not_overwritten(self) -> None:
        legacy = {
            "version": 5,
            "buttons": {
                "LB": {"action": "tmux_keys", "command": "select-pane -L"},
                "RB": {"action": "tmux_keys", "command": "select-pane -R"},
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(legacy), encoding="utf-8")

            config = load_config(path)

        self.assertEqual(config["buttons"]["LB"]["command"], "select-pane -L")
        self.assertEqual(config["buttons"]["RB"]["command"], "select-pane -R")
        self.assertEqual(config["buttons"]["LB"]["action"], "tmux")

    def test_old_start_pause_setting_is_removed_and_text_mapping_is_added(self) -> None:
        legacy = {
            "version": 7,
            "general": {"start_hold_seconds": 2.0},
            "buttons": {"START": {"action": "toggle_mapping"}},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(json.dumps(legacy), encoding="utf-8")

            config = load_config(path)

        self.assertNotIn("start_hold_seconds", config["general"])
        self.assertEqual(config["buttons"]["START"]["action"], "text")
        self.assertEqual(
            config["buttons"]["START"]["text"],
            "在本分支commit & push代码，然后温和重启项目",
        )


if __name__ == "__main__":
    unittest.main()
