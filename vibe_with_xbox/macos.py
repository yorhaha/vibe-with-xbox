from __future__ import annotations

import subprocess
from collections.abc import Iterable

KEYCODES = {
    "a": 0x00,
    "b": 0x0B,
    "c": 0x08,
    "d": 0x02,
    "e": 0x0E,
    "f": 0x03,
    "g": 0x05,
    "h": 0x04,
    "i": 0x22,
    "j": 0x26,
    "k": 0x28,
    "l": 0x25,
    "m": 0x2E,
    "n": 0x2D,
    "o": 0x1F,
    "p": 0x23,
    "q": 0x0C,
    "r": 0x0F,
    "s": 0x01,
    "t": 0x11,
    "u": 0x20,
    "v": 0x09,
    "w": 0x0D,
    "x": 0x07,
    "y": 0x10,
    "z": 0x06,
    "return": 0x24,
    "enter": 0x24,
    "escape": 0x35,
    "esc": 0x35,
    "up": 0x7E,
    "down": 0x7D,
    "f5": 0x60,
    "option": 0x3A,
    "alt": 0x3A,
    "right_option": 0x3D,
    "right_alt": 0x3D,
}

# CGEventFlags values are stable API constants. Keeping them here lets config
# validation and tests run without importing Quartz on non-macOS systems.
MODIFIER_FLAGS = {
    "shift": 0x00020000,
    "control": 0x00040000,
    "ctrl": 0x00040000,
    "option": 0x00080000,
    "alt": 0x00080000,
    "command": 0x00100000,
    "cmd": 0x00100000,
    "function": 0x00800000,
    "fn": 0x00800000,
}
MODIFIER_KEY_FLAGS = {
    "option": MODIFIER_FLAGS["option"],
    "alt": MODIFIER_FLAGS["alt"],
    "right_option": MODIFIER_FLAGS["option"],
    "right_alt": MODIFIER_FLAGS["alt"],
}

class KeySendError(RuntimeError):
    pass


def resolve_keycode(key: str | int) -> int:
    if isinstance(key, int):
        return key
    normalized = key.lower().strip()
    if normalized not in KEYCODES:
        raise KeySendError(f"不支持的按键名称：{key}")
    return KEYCODES[normalized]


def resolve_modifier_flags(modifiers: Iterable[str] | str | None) -> int:
    if modifiers is None:
        return 0
    names = [modifiers] if isinstance(modifiers, str) else modifiers
    flags = 0
    for modifier in names:
        normalized = modifier.lower().strip()
        if normalized not in MODIFIER_FLAGS:
            raise KeySendError(f"不支持的修饰键名称：{modifier}")
        flags |= MODIFIER_FLAGS[normalized]
    return flags


def _post_key_event(
    key: str | int,
    is_down: bool,
    flags: int = 0,
    modifiers: Iterable[str] | str | None = None,
) -> None:
    try:
        from Quartz import (  # type: ignore
            CGEventCreateKeyboardEvent,
            CGEventPost,
            CGEventSetFlags,
            kCGHIDEventTap,
        )
    except Exception as exc:  # pragma: no cover - only reachable on missing macOS deps
        raise KeySendError("Quartz 不可用，请安装 pyobjc-framework-Quartz。") from exc

    keycode = resolve_keycode(key)
    flags |= resolve_modifier_flags(modifiers)
    if is_down and isinstance(key, str):
        flags |= MODIFIER_KEY_FLAGS.get(key.lower().strip(), 0)
    event = CGEventCreateKeyboardEvent(None, keycode, is_down)
    if flags:
        CGEventSetFlags(event, flags)
    CGEventPost(kCGHIDEventTap, event)


def key_down(
    key: str | int,
    flags: int = 0,
    modifiers: Iterable[str] | str | None = None,
) -> None:
    _post_key_event(key, True, flags, modifiers)


def key_up(
    key: str | int,
    flags: int = 0,
    modifiers: Iterable[str] | str | None = None,
) -> None:
    _post_key_event(key, False, flags, modifiers)


def tap_key(
    key: str | int,
    flags: int = 0,
    modifiers: Iterable[str] | str | None = None,
) -> None:
    key_down(key, flags, modifiers)
    key_up(key, flags, modifiers)


def type_text(text: str) -> None:
    """Type literal text into the focused app using Quartz keyboard events."""
    if not text:
        return
    try:
        from Quartz import (  # type: ignore
            CGEventCreateKeyboardEvent,
            CGEventKeyboardSetUnicodeString,
            CGEventPost,
            kCGHIDEventTap,
        )
    except Exception as exc:  # pragma: no cover - only reachable on missing macOS deps
        raise KeySendError("Quartz 不可用，请安装 pyobjc-framework-Quartz。") from exc

    down = CGEventCreateKeyboardEvent(None, 0, True)
    up = CGEventCreateKeyboardEvent(None, 0, False)
    utf16_length = len(text.encode("utf-16-le")) // 2
    CGEventKeyboardSetUnicodeString(down, utf16_length, text)
    CGEventKeyboardSetUnicodeString(up, utf16_length, text)
    CGEventPost(kCGHIDEventTap, down)
    CGEventPost(kCGHIDEventTap, up)


def accessibility_trusted() -> tuple[bool | None, str]:
    try:
        from ApplicationServices import AXIsProcessTrusted  # type: ignore
    except Exception:
        return None, "当前 Python 运行环境无法检查辅助功能权限。"
    return bool(AXIsProcessTrusted()), "辅助功能权限已启用，可以向其他应用发送按键。"


def open_accessibility_settings() -> None:
    subprocess.run(
        [
            "open",
            "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
        ],
        check=False,
    )
