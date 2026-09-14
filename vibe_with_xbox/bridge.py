from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable

from . import macos
from .config import AXIS_INDEXES, BUTTON_INDEXES, CONTROL_NAMES, mapping_for_control
from .tmux_control import TmuxController

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

BridgeCallback = Callable[["BridgeEvent"], None]


@dataclass
class BridgeEvent:
    kind: str
    control: str | None = None
    value: float | None = None
    message: str = ""
    action_label: str = ""


class ControllerBridge:
    def __init__(
        self,
        config: dict[str, Any],
        callback: BridgeCallback | None = None,
        debug: bool = False,
        send_actions: bool = True,
    ) -> None:
        self.config = config
        self.callback = callback
        self.debug = debug
        self.send_actions = send_actions
        self.stop_event = threading.Event()
        self.tmux = TmuxController()
        self._held_keys: dict[str, str | int] = {}
        self._held_keys_lock = threading.Lock()

        general = config.get("general", {})
        self.deadzone = float(general.get("deadzone", 0.5))
        self.trigger_threshold = float(general.get("trigger_threshold", 0.2))
        self.repeat_initial_delay = float(general.get("repeat_initial_delay", 0.35))
        self.repeat_rate = float(general.get("repeat_rate", 0.08))

        self._stick_dir = 0
        self._stick_next_fire = 0.0
        self._right_stick_control: str | None = None
        self._rt_pressed_at: float | None = None
        self._rt_fired = False

    def stop(self) -> None:
        self.stop_event.set()
        self._release_all_held_keys()
        self._release_right_stick()

    def emit(self, event: BridgeEvent) -> None:
        if self.callback:
            self.callback(event)

    def run(self) -> int:
        try:
            import pygame
        except Exception as exc:
            self.emit(BridgeEvent("error", message=f"pygame 不可用：{exc}"))
            return 1

        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            self.emit(
                BridgeEvent(
                    "error",
                    message="未检测到手柄，请连接 Xbox 手柄后重试。",
                )
            )
            return 1

        joystick = pygame.joystick.Joystick(0)
        try:
            joystick.init()
            self.emit(
                BridgeEvent(
                    "connected",
                    message=(
                        f"已连接：{joystick.get_name()} "
                        f"（{joystick.get_numaxes()} 个轴，{joystick.get_numbuttons()} 个按键）"
                    ),
                )
            )

            clock = pygame.time.Clock()
            while not self.stop_event.is_set():
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return 0
                    if event.type == pygame.JOYBUTTONDOWN:
                        self._handle_button_down(event.button)
                    elif event.type == pygame.JOYBUTTONUP:
                        self._handle_button_up(event.button)
                    elif event.type == pygame.JOYAXISMOTION and self.debug:
                        if abs(event.value) > self.deadzone:
                            self.emit(
                                BridgeEvent(
                                    "debug",
                                    value=float(event.value),
                                    message=f"axis {event.axis}: {event.value:+.2f}",
                                )
                            )

                if not self.debug:
                    self._poll_left_stick(joystick)
                    self._poll_right_stick(joystick)
                    self._poll_rt(joystick)
                clock.tick(120)
        finally:
            self._release_all_held_keys()
            self._release_right_stick()
            joystick.quit()
            pygame.joystick.quit()
            pygame.quit()

        self.emit(BridgeEvent("stopped", message="手柄映射已停止。"))
        return 0

    def _control_for_button(self, button_index: int) -> str | None:
        for control, index in BUTTON_INDEXES.items():
            if index == button_index:
                return control
        return None

    def _handle_button_down(self, button_index: int) -> None:
        control = self._control_for_button(button_index)
        if self.debug:
            self.emit(BridgeEvent("debug", control=control, message=f"按键按下：{button_index}"))
            return
        if control is None:
            self.emit(BridgeEvent("input", message=f"按键 {button_index}"))
            return

        self.emit(BridgeEvent("down", control=control, message=CONTROL_NAMES.get(control, control)))
        self.perform_control(control)

    def _handle_button_up(self, button_index: int) -> None:
        control = self._control_for_button(button_index)
        if self.debug:
            self.emit(BridgeEvent("debug", control=control, message=f"按键松开：{button_index}"))
            return
        if control:
            self.emit(BridgeEvent("up", control=control, message=CONTROL_NAMES.get(control, control)))
            self._release_held_key(control)

    def _poll_left_stick(self, joystick: Any) -> None:
        y = float(joystick.get_axis(AXIS_INDEXES["LEFT_STICK_Y"]))
        now = time.monotonic()
        if y < -self.deadzone:
            new_dir, control = -1, "LEFT_STICK_UP"
        elif y > self.deadzone:
            new_dir, control = 1, "LEFT_STICK_DOWN"
        else:
            new_dir, control = 0, None

        if new_dir != self._stick_dir:
            previous = "LEFT_STICK_UP" if self._stick_dir < 0 else "LEFT_STICK_DOWN"
            if self._stick_dir != 0:
                self.emit(BridgeEvent("up", control=previous))
            self._stick_dir = new_dir
            if control is not None:
                self.emit(BridgeEvent("down", control=control, value=y))
                self.perform_control(control)
                self._stick_next_fire = now + self.repeat_initial_delay
        elif control is not None and now >= self._stick_next_fire:
            self.emit(BridgeEvent("pulse", control=control, value=y))
            self.perform_control(control)
            self._stick_next_fire = now + self.repeat_rate

    def _poll_rt(self, joystick: Any) -> None:
        rt_now = float(joystick.get_axis(AXIS_INDEXES["RT"])) > self.trigger_threshold
        now = time.monotonic()
        mapping = mapping_for_control(self.config, "RT")
        hold_seconds = float(mapping.get("hold_seconds", 0.7))

        if rt_now and self._rt_pressed_at is None:
            self._rt_pressed_at = now
            self._rt_fired = False
            self.emit(BridgeEvent("down", control="RT"))
            return

        if not rt_now and self._rt_pressed_at is not None:
            self.emit(BridgeEvent("up", control="RT"))
            self._rt_pressed_at = None
            self._rt_fired = False
            return

        if rt_now and self._rt_pressed_at is not None and not self._rt_fired:
            held = now - self._rt_pressed_at
            if held >= hold_seconds:
                self._rt_fired = True
                self.perform_control("RT")

    def _poll_right_stick(self, joystick: Any) -> None:
        x = float(joystick.get_axis(AXIS_INDEXES["RIGHT_STICK_X"]))
        y = float(joystick.get_axis(AXIS_INDEXES["RIGHT_STICK_Y"]))
        if abs(x) <= self.deadzone and abs(y) <= self.deadzone:
            self._release_right_stick()
            return

        # One deflection performs one pane change. The stick must return to
        # center before another direction can fire, preventing rapid skips.
        if self._right_stick_control is not None:
            return
        if abs(x) > abs(y):
            control = "RIGHT_STICK_LEFT" if x < 0 else "RIGHT_STICK_RIGHT"
            value = x
        else:
            control = "RIGHT_STICK_UP" if y < 0 else "RIGHT_STICK_DOWN"
            value = y
        self._right_stick_control = control
        self.emit(BridgeEvent("down", control=control, value=value))
        self.perform_control(control)

    def _release_right_stick(self) -> None:
        if self._right_stick_control is None:
            return
        self.emit(BridgeEvent("up", control=self._right_stick_control))
        self._right_stick_control = None

    def perform_control(self, control: str) -> None:
        mapping = mapping_for_control(self.config, control)
        if not mapping.get("enabled", True):
            return
        label = str(mapping.get("label", control))
        self.emit(BridgeEvent("action", control=control, action_label=label, message=label))
        if not self.send_actions:
            return

        try:
            self._perform_mapping(mapping, control)
        except Exception as exc:
            self.emit(BridgeEvent("error", control=control, message=str(exc), action_label=label))

    def _perform_mapping(self, mapping: dict[str, Any], control: str | None = None) -> None:
        action = mapping.get("action")
        if action == "key":
            macos.tap_key(mapping["key"])
        elif action == "text":
            macos.type_text(str(mapping.get("text", "")))
        elif action == "sequence":
            gap = float(mapping.get("gap", 0.04))
            for key in mapping.get("keys", []):
                macos.tap_key(key)
                time.sleep(gap)
        elif action == "hold_key":
            if control is None:
                raise RuntimeError("hold_key 操作必须关联一个手柄输入")
            key = mapping["key"]
            with self._held_keys_lock:
                if self.stop_event.is_set():
                    return
                if control not in self._held_keys:
                    macos.key_down(key)
                    self._held_keys[control] = key
        elif action == "tmux":
            args = mapping.get("args")
            if args is not None:
                command = " ".join(str(arg) for arg in args)
            else:
                command = str(mapping.get("command", ""))
            self.tmux.send_command(command)
        elif action == "none":
            return
        else:
            raise RuntimeError(f"未知操作类型：{action}")

    def _release_held_key(self, control: str) -> None:
        with self._held_keys_lock:
            key = self._held_keys.pop(control, None)
            if key is not None:
                macos.key_up(key)

    def _release_all_held_keys(self) -> None:
        with self._held_keys_lock:
            keys = list(self._held_keys.values())
            self._held_keys.clear()
        for key in keys:
            macos.key_up(key)
