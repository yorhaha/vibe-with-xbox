from __future__ import annotations

import subprocess

KEYCODES = {
    "return": 0x24,
    "enter": 0x24,
    "escape": 0x35,
    "esc": 0x35,
    "up": 0x7E,
    "down": 0x7D,
    "f5": 0x60,
}


class KeySendError(RuntimeError):
    pass


def resolve_keycode(key: str | int) -> int:
    if isinstance(key, int):
        return key
    normalized = key.lower().strip()
    if normalized not in KEYCODES:
        raise KeySendError(f"Unsupported key name: {key}")
    return KEYCODES[normalized]


def tap_key(key: str | int, flags: int = 0) -> None:
    try:
        from Quartz import (  # type: ignore
            CGEventCreateKeyboardEvent,
            CGEventPost,
            CGEventSetFlags,
            kCGHIDEventTap,
        )
    except Exception as exc:  # pragma: no cover - only reachable on missing macOS deps
        raise KeySendError("Quartz is unavailable; install pyobjc-framework-Quartz.") from exc

    keycode = resolve_keycode(key)
    down = CGEventCreateKeyboardEvent(None, keycode, True)
    up = CGEventCreateKeyboardEvent(None, keycode, False)
    if flags:
        CGEventSetFlags(down, flags)
        CGEventSetFlags(up, flags)
    CGEventPost(kCGHIDEventTap, down)
    CGEventPost(kCGHIDEventTap, up)


def accessibility_trusted() -> tuple[bool | None, str]:
    try:
        from ApplicationServices import AXIsProcessTrusted  # type: ignore
    except Exception:
        return None, "Cannot check Accessibility permission on this Python runtime."
    return bool(AXIsProcessTrusted()), "Accessibility permission can send keys to other apps."


def open_accessibility_settings() -> None:
    subprocess.run(
        [
            "open",
            "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
        ],
        check=False,
    )
