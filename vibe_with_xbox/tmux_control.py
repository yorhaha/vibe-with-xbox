from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class TmuxResult:
    ok: bool
    message: str


class TmuxController:
    def __init__(self) -> None:
        self.path = shutil.which("tmux")
        self.warned = False

    def run(self, *args: str) -> TmuxResult:
        if self.path is None:
            return TmuxResult(False, "tmux not found on PATH; pane controls are disabled.")
        result = subprocess.run(
            [self.path, *args],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return TmuxResult(True, f"tmux {' '.join(args)}")
        msg = result.stderr.strip() or "tmux command failed"
        return TmuxResult(False, f"tmux {' '.join(args)}: {msg}")

    def check(self) -> TmuxResult:
        if self.path is None:
            return TmuxResult(False, "tmux is not installed or not on PATH.")
        result = subprocess.run(
            [self.path, "list-sessions"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return TmuxResult(True, "tmux is installed and at least one session is running.")
        return TmuxResult(
            False,
            result.stderr.strip() or "tmux is installed, but no tmux server is running.",
        )
