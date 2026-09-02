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
    enabled: bool | None = None


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
        self.enabled = True
        self.tmux = TmuxController()

        general = config.get("general", {})
        self.deadzone = float(general.get("deadzone", 0.5))
        self.trigger_threshold = float(general.get("trigger_threshold", 0.2))
        self.repeat_initial_delay = float(general.get("repeat_initial_delay", 0.35))
        self.repeat_rate = float(general.get("repeat_rate", 0.08))
        self.start_hold_seconds = float(general.get("start_hold_seconds", 1.0))

        self._start_pressed_at: float | None = None
        self._stick_dir = 0
        self._stick_next_fire = 0.0
        self._rt_pressed_at: float | None = None
        self._rt_fired = False

    def stop(self) -> None:
        self.stop_event.set()

    def emit(self, event: BridgeEvent) -> None:
        if self.callback:
            self.callback(event)

    def run(self) -> int:
        try:
            import pygame
        except Exception as exc:
            self.emit(BridgeEvent("error", message=f"pygame is unavailable: {exc}"))
            return 1

        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            self.emit(
                BridgeEvent(
                    "error",
                    message="No controller detected. Pair your Xbox controller and try again.",
                )
            )
            return 1

        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        self.emit(
            BridgeEvent(
                "connected",
                message=(
                    f"Connected: {joystick.get_name()} "
                    f"({joystick.get_numaxes()} axes, {joystick.get_numbuttons()} buttons)"
                ),
                enabled=self.enabled,
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

            if not self.debug and self.enabled:
                self._poll_left_stick(joystick)
                self._poll_rt(joystick)
            clock.tick(120)

        self.emit(BridgeEvent("stopped", message="Controller bridge stopped."))
        return 0

    def _control_for_button(self, button_index: int) -> str | None:
        for control, index in BUTTON_INDEXES.items():
            if index == button_index:
                return control
        return None

    def _handle_button_down(self, button_index: int) -> None:
        control = self._control_for_button(button_index)
        if self.debug:
            self.emit(BridgeEvent("debug", control=control, message=f"button DOWN: {button_index}"))
            return
        if control is None:
            self.emit(BridgeEvent("input", message=f"button {button_index}"))
            return

        self.emit(BridgeEvent("down", control=control, message=CONTROL_NAMES.get(control, control)))

        if control == "START":
            self._start_pressed_at = time.monotonic()
            return
        if not self.enabled:
            return
        self.perform_control(control)

    def _handle_button_up(self, button_index: int) -> None:
        control = self._control_for_button(button_index)
        if self.debug:
            self.emit(BridgeEvent("debug", control=control, message=f"button UP:   {button_index}"))
            return
        if control:
            self.emit(BridgeEvent("up", control=control, message=CONTROL_NAMES.get(control, control)))
        if control == "START" and self._start_pressed_at is not None:
            held = time.monotonic() - self._start_pressed_at
            if held >= self.start_hold_seconds:
                self.enabled = not self.enabled
                self.emit(
                    BridgeEvent(
                        "toggle",
                        control="START",
                        message=f"Mapping {'enabled' if self.enabled else 'paused'}",
                        enabled=self.enabled,
                    )
                )
            self._start_pressed_at = None

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

    def perform_control(self, control: str) -> None:
        mapping = mapping_for_control(self.config, control)
        if not mapping.get("enabled", True):
            return
        label = str(mapping.get("label", control))
        self.emit(BridgeEvent("action", control=control, action_label=label, message=label))
        if not self.send_actions:
            return

        try:
            self._perform_mapping(mapping)
        except Exception as exc:
            self.emit(BridgeEvent("error", control=control, message=str(exc), action_label=label))

    def _perform_mapping(self, mapping: dict[str, Any]) -> None:
        action = mapping.get("action")
        if action == "key":
            macos.tap_key(mapping["key"])
        elif action == "sequence":
            gap = float(mapping.get("gap", 0.04))
            for key in mapping.get("keys", []):
                macos.tap_key(key)
                time.sleep(gap)
        elif action == "dictation":
            macos_cfg = self.config.get("macos", {})
            macos.tap_key(
                macos_cfg.get("dictation_key", "f5"),
                int(macos_cfg.get("dictation_flags", 0)),
            )
        elif action == "tmux":
            args = [str(arg) for arg in mapping.get("args", [])]
            result = self.tmux.run(*args)
            if not result.ok:
                self.emit(BridgeEvent("warning", message=result.message))
        elif action in {"none", "toggle_mapping"}:
            return
        else:
            raise RuntimeError(f"Unknown action type: {action}")
