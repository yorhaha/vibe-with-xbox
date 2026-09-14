from __future__ import annotations

import unittest
from types import ModuleType
from unittest.mock import patch

from vibe_with_xbox.macos import (
    KeySendError,
    resolve_keycode,
    resolve_modifier_flags,
    key_down,
    key_up,
    type_text,
)


class MacOSKeyTests(unittest.TestCase):
    def test_resolves_left_and_right_option_keycodes(self) -> None:
        self.assertEqual(resolve_keycode("option"), 0x3A)
        self.assertEqual(resolve_keycode("right_option"), 0x3D)

    def test_resolves_letter_keycode_for_custom_tmux_prefix(self) -> None:
        self.assertEqual(resolve_keycode("a"), 0x00)

    def test_combines_named_modifier_flags(self) -> None:
        self.assertEqual(
            resolve_modifier_flags(["control", "shift"]),
            0x00040000 | 0x00020000,
        )

    def test_rejects_unknown_modifier(self) -> None:
        with self.assertRaisesRegex(KeySendError, "不支持的修饰键"):
            resolve_modifier_flags(["hyper"])

    def test_option_key_down_sets_modifier_flag_and_key_up_clears_it(self) -> None:
        calls: list[tuple] = []
        quartz = ModuleType("Quartz")
        quartz.kCGHIDEventTap = 7  # type: ignore[attr-defined]
        quartz.CGEventCreateKeyboardEvent = (  # type: ignore[attr-defined]
            lambda _source, keycode, down: [keycode, down]
        )
        quartz.CGEventSetFlags = (  # type: ignore[attr-defined]
            lambda event, flags: calls.append(("flags", tuple(event), flags))
        )
        quartz.CGEventPost = (  # type: ignore[attr-defined]
            lambda tap, event: calls.append(("post", tap, tuple(event)))
        )

        with patch.dict("sys.modules", {"Quartz": quartz}):
            key_down("option")
            key_up("option")

        self.assertEqual(
            calls,
            [
                ("flags", (0x3A, True), 0x00080000),
                ("post", 7, (0x3A, True)),
                ("post", 7, (0x3A, False)),
            ],
        )

    def test_right_option_uses_right_keycode(self) -> None:
        calls: list[tuple] = []
        quartz = ModuleType("Quartz")
        quartz.kCGHIDEventTap = 7  # type: ignore[attr-defined]
        quartz.CGEventCreateKeyboardEvent = (  # type: ignore[attr-defined]
            lambda _source, keycode, down: [keycode, down]
        )
        quartz.CGEventSetFlags = (  # type: ignore[attr-defined]
            lambda event, flags: calls.append(("flags", tuple(event), flags))
        )
        quartz.CGEventPost = (  # type: ignore[attr-defined]
            lambda tap, event: calls.append(("post", tap, tuple(event)))
        )

        with patch.dict("sys.modules", {"Quartz": quartz}):
            key_down("right_option")
            key_up("right_option")

        self.assertEqual(
            calls,
            [
                ("flags", (0x3D, True), 0x00080000),
                ("post", 7, (0x3D, True)),
                ("post", 7, (0x3D, False)),
            ],
        )

    def test_type_text_posts_unicode_events_with_utf16_length(self) -> None:
        calls: list[tuple] = []
        quartz = ModuleType("Quartz")
        quartz.kCGHIDEventTap = 7  # type: ignore[attr-defined]
        quartz.CGEventCreateKeyboardEvent = (  # type: ignore[attr-defined]
            lambda _source, keycode, down: (keycode, down)
        )
        quartz.CGEventKeyboardSetUnicodeString = (  # type: ignore[attr-defined]
            lambda event, length, value: calls.append(("text", event, length, value))
        )
        quartz.CGEventPost = (  # type: ignore[attr-defined]
            lambda tap, event: calls.append(("post", tap, event))
        )

        with patch.dict("sys.modules", {"Quartz": quartz}):
            type_text("A😀")

        self.assertEqual(
            calls,
            [
                ("text", (0, True), 3, "A😀"),
                ("text", (0, False), 3, "A😀"),
                ("post", 7, (0, True)),
                ("post", 7, (0, False)),
            ],
        )


if __name__ == "__main__":
    unittest.main()
