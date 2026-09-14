from __future__ import annotations

import copy
import unittest
from unittest.mock import patch

from vibe_with_xbox.bridge import ControllerBridge
from vibe_with_xbox.config import DEFAULT_CONFIG


class FakeTmuxSender:
    def __init__(self) -> None:
        self.commands: list[str] = []

    def send_command(self, command: str) -> None:
        self.commands.append(command)


class BridgeTmuxMappingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bridge = ControllerBridge(copy.deepcopy(DEFAULT_CONFIG))
        self.sender = FakeTmuxSender()
        self.bridge.tmux = self.sender  # type: ignore[assignment]

    def test_tmux_command_mapping_uses_local_controller(self) -> None:
        self.bridge._perform_mapping(
            {"action": "tmux", "command": "split-window -v -b"}
        )

        self.assertEqual(self.sender.commands, ["split-window -v -b"])

    def test_version_one_tmux_mapping_remains_compatible(self) -> None:
        self.bridge._perform_mapping(
            {"action": "tmux", "args": ["select-pane", "-t", ":.-"]}
        )

        self.assertEqual(self.sender.commands, ["select-pane -t :.-"])


class BridgeTextMappingTests(unittest.TestCase):
    @patch("vibe_with_xbox.bridge.macos.type_text")
    def test_start_types_restart_instruction_once_on_button_down(self, type_text) -> None:
        events = []
        bridge = ControllerBridge(copy.deepcopy(DEFAULT_CONFIG), callback=events.append)

        bridge._handle_button_down(6)
        bridge._handle_button_up(6)

        type_text.assert_called_once_with("在本分支commit & push代码，然后温和重启项目")
        self.assertEqual(
            [event.kind for event in events if event.control == "START"],
            ["down", "action", "up"],
        )


class BridgeHeldKeyMappingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bridge = ControllerBridge(copy.deepcopy(DEFAULT_CONFIG))

    @patch("vibe_with_xbox.bridge.macos.key_up")
    @patch("vibe_with_xbox.bridge.macos.key_down")
    def test_x_holds_right_option_until_button_up(self, key_down, key_up) -> None:
        self.bridge._handle_button_down(2)
        key_down.assert_called_once_with("right_option")
        key_up.assert_not_called()

        self.bridge._handle_button_up(2)
        key_up.assert_called_once_with("right_option")

    @patch("vibe_with_xbox.bridge.macos.key_up")
    @patch("vibe_with_xbox.bridge.macos.key_down")
    def test_stop_releases_held_right_option(self, key_down, key_up) -> None:
        self.bridge._handle_button_down(2)

        self.bridge.stop()

        key_down.assert_called_once_with("right_option")
        key_up.assert_called_once_with("right_option")


class FakeJoystick:
    def __init__(self) -> None:
        self.axes = {2: 0.0, 3: 0.0}

    def get_axis(self, index: int) -> float:
        return self.axes.get(index, 0.0)


class BridgeRightStickTests(unittest.TestCase):
    def setUp(self) -> None:
        self.events = []
        self.bridge = ControllerBridge(copy.deepcopy(DEFAULT_CONFIG), callback=self.events.append)
        self.sender = FakeTmuxSender()
        self.bridge.tmux = self.sender  # type: ignore[assignment]
        self.joystick = FakeJoystick()

    def move(self, x: float, y: float) -> None:
        self.joystick.axes.update({2: x, 3: y})
        self.bridge._poll_right_stick(self.joystick)

    def test_each_direction_selects_spatial_tmux_pane(self) -> None:
        for x, y in ((0, -1), (0, 1), (-1, 0), (1, 0)):
            self.move(x, y)
            self.move(0, 0)

        self.assertEqual(
            self.sender.commands,
            ["select-pane -U", "select-pane -D", "select-pane -L", "select-pane -R"],
        )

    def test_holding_stick_fires_only_once_until_centered(self) -> None:
        self.move(1, 0)
        self.move(1, 0)
        self.move(0.9, 0.2)

        self.assertEqual(self.sender.commands, ["select-pane -R"])

        self.move(0, 0)
        self.move(1, 0)
        self.assertEqual(self.sender.commands, ["select-pane -R", "select-pane -R"])

    def test_dominant_axis_wins_for_diagonal_input(self) -> None:
        self.move(-0.7, 0.9)

        self.assertEqual(self.sender.commands, ["select-pane -D"])

if __name__ == "__main__":
    unittest.main()
