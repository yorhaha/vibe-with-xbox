from __future__ import annotations

import os
from dataclasses import dataclass

from . import macos
from .tmux_control import TmuxController

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")


@dataclass
class CheckResult:
    name: str
    status: str
    message: str


def check_controller() -> CheckResult:
    pygame = None
    try:
        import pygame

        pygame.init()
        pygame.joystick.init()
        count = pygame.joystick.get_count()
        if count <= 0:
            return CheckResult(
                "Controller",
                "fail",
                "No controller detected. Pair an Xbox controller over Bluetooth.",
            )
        js = pygame.joystick.Joystick(0)
        js.init()
        return CheckResult(
            "Controller",
            "ok",
            f"{js.get_name()} detected ({js.get_numaxes()} axes, {js.get_numbuttons()} buttons).",
        )
    except Exception as exc:
        return CheckResult("Controller", "fail", f"Cannot read controller: {exc}")
    finally:
        if pygame is not None:
            try:
                pygame.joystick.quit()
                pygame.quit()
            except Exception:
                pass


def check_accessibility() -> CheckResult:
    trusted, message = macos.accessibility_trusted()
    if trusted is True:
        return CheckResult("Accessibility", "ok", message)
    if trusted is False:
        return CheckResult(
            "Accessibility",
            "fail",
            "Grant Accessibility permission so Vibe with Xbox can send keys.",
        )
    return CheckResult("Accessibility", "warn", message)


def check_tmux() -> CheckResult:
    result = TmuxController().check()
    return CheckResult("tmux", "ok" if result.ok else "warn", result.message)


def check_dictation() -> CheckResult:
    return CheckResult(
        "Dictation",
        "warn",
        "macOS does not expose this shortcut reliably; set Dictation shortcut to F5.",
    )


def run_checks() -> list[CheckResult]:
    return [
        check_controller(),
        check_accessibility(),
        check_tmux(),
        check_dictation(),
    ]
