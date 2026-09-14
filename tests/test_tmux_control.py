from __future__ import annotations

import subprocess
import unittest
from unittest.mock import call, patch

from vibe_with_xbox.tmux_control import TmuxController


class TmuxControllerTests(unittest.TestCase):
    @patch("vibe_with_xbox.tmux_control.shutil.which", return_value="/usr/bin/tmux")
    @patch("vibe_with_xbox.tmux_control.subprocess.run")
    def test_send_command_always_uses_local_tmux_cli(self, run, _which) -> None:
        run.return_value = subprocess.CompletedProcess([], 0, stdout="", stderr="")
        controller = TmuxController()

        result = controller.send_command("split-window -v -b")

        self.assertTrue(result.ok)
        run.assert_called_once_with(
            ["/usr/bin/tmux", "split-window", "-v", "-b"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

    @patch("vibe_with_xbox.tmux_control.shutil.which", return_value=None)
    def test_send_command_reports_missing_local_tmux(self, _which) -> None:
        controller = TmuxController()

        with self.assertRaisesRegex(RuntimeError, "未在 PATH 中找到 tmux"):
            controller.send_command("kill-pane")

    @patch("vibe_with_xbox.tmux_control.shutil.which", return_value="/usr/bin/tmux")
    def test_send_command_rejects_multiline_input(self, _which) -> None:
        with self.assertRaisesRegex(ValueError, "单行文本"):
            TmuxController().send_command("kill-pane\nrun-shell bad")


if __name__ == "__main__":
    unittest.main()
