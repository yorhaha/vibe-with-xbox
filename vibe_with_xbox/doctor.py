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
                "手柄",
                "fail",
                "未检测到手柄，请通过蓝牙连接 Xbox 手柄。",
            )
        js = pygame.joystick.Joystick(0)
        js.init()
        return CheckResult(
            "手柄",
            "ok",
            f"已检测到 {js.get_name()}（{js.get_numaxes()} 个轴，{js.get_numbuttons()} 个按键）。",
        )
    except Exception as exc:
        return CheckResult("手柄", "fail", f"无法读取手柄：{exc}")
    finally:
        if pygame is not None:
            pygame.joystick.quit()
            pygame.quit()


def check_accessibility() -> CheckResult:
    trusted, message = macos.accessibility_trusted()
    if trusted is True:
        return CheckResult("辅助功能权限", "ok", message)
    if trusted is False:
        return CheckResult(
            "辅助功能权限",
            "fail",
            "请授予辅助功能权限，以便 Vibe with Xbox 向其他应用发送按键。",
        )
    return CheckResult("辅助功能权限", "warn", message)


def check_tmux() -> CheckResult:
    result = TmuxController().check()
    return CheckResult("tmux", "ok" if result.ok else "warn", result.message)


def run_checks() -> list[CheckResult]:
    return [
        check_controller(),
        check_accessibility(),
        check_tmux(),
    ]
