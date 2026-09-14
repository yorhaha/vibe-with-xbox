from __future__ import annotations

import copy
import threading
import unittest
from unittest.mock import patch

from vibe_with_xbox.config import DEFAULT_CONFIG, guide_rows
from vibe_with_xbox.ui import LocalGuideApp, render_index


class ChineseUiTests(unittest.TestCase):
    def test_page_uses_chinese_interface_copy(self) -> None:
        html = render_index(copy.deepcopy(DEFAULT_CONFIG))

        for text in (
            'lang="zh-CN"',
            "启动手柄映射",
            "运行环境检查",
            "当前映射",
            "环境检查",
            "尚未启动",
            "暂无手柄操作",
            "长按 RT",
        ):
            self.assertIn(text, html)

        for text in (
            "Start Bridge",
            "Run Checks",
            "Current Mapping",
            "Setup Checks",
            "Not started",
            "No controller action yet",
            # The mapping pause toggle was removed; the status field that
            # reported it is gone too.
            "映射状态",
        ):
            self.assertNotIn(text, html)

    def test_default_mapping_copy_is_chinese(self) -> None:
        rows = {row["control"]: row for row in guide_rows(copy.deepcopy(DEFAULT_CONFIG))}

        self.assertEqual(rows["X"]["label"], "按住右 Option")
        self.assertEqual(rows["DPAD_UP"]["name"], "十字键上")
        self.assertEqual(rows["LB"]["label"], "上一个会话")
        self.assertEqual(rows["RIGHT_STICK_LEFT"]["label"], "切换到左侧窗格")
        self.assertEqual(rows["START"]["label"], "粘贴重启指令")


class GuiThreadingTests(unittest.TestCase):
    def test_bridge_runs_on_gui_process_main_thread(self) -> None:
        bridge_started = threading.Event()
        bridge_threads: list[int] = []

        class FakeBridge:
            def __init__(self, config, callback=None) -> None:
                self.stop_event = threading.Event()

            def run(self) -> int:
                bridge_threads.append(threading.get_ident())
                bridge_started.set()
                self.stop_event.wait(2)
                return 0

            def stop(self) -> None:
                self.stop_event.set()

        with (
            patch("vibe_with_xbox.ui.ControllerBridge", FakeBridge),
            patch("vibe_with_xbox.ui.run_checks", return_value=[]),
        ):
            app = LocalGuideApp(port=0)
            app.start_bridge()

            def request_quit() -> None:
                self.assertTrue(bridge_started.wait(1))
                app.quit()

            helper = threading.Thread(target=request_quit)
            helper.start()
            caller_thread = threading.get_ident()
            result = app.run(open_browser=False)
            helper.join(timeout=1)

        self.assertEqual(result, 0)
        self.assertEqual(bridge_threads, [caller_thread])
        self.assertFalse(helper.is_alive())


if __name__ == "__main__":
    unittest.main()
