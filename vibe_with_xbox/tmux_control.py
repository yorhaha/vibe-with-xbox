from __future__ import annotations

import shlex
import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class TmuxResult:
    ok: bool
    message: str


class TmuxController:
    """Run commands against the local tmux server."""

    def __init__(self) -> None:
        self.path = shutil.which("tmux")

    def send_command(self, command: str) -> TmuxResult:
        command = command.strip()
        if not command:
            raise ValueError("tmux 命令不能为空")
        if "\n" in command or "\r" in command:
            raise ValueError("tmux 命令必须为单行文本")
        try:
            args = shlex.split(command)
        except ValueError as exc:
            raise ValueError(f"无法解析 tmux 命令：{exc}") from exc
        if not args:
            raise ValueError("tmux 命令不能为空")

        result = self.run(*args)
        if not result.ok:
            raise RuntimeError(result.message)
        return result

    def run(self, *args: str) -> TmuxResult:
        if self.path is None:
            return TmuxResult(False, "未在 PATH 中找到 tmux，本地窗格操作不可用。")
        result = subprocess.run(
            [self.path, *args],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return TmuxResult(True, f"tmux {' '.join(args)}")
        message = result.stderr.strip() or "tmux 命令执行失败"
        return TmuxResult(False, f"tmux {' '.join(args)}：{message}")

    def has_attached_client(self) -> bool:
        if self.path is None:
            return False
        result = subprocess.run(
            [self.path, "list-clients", "-F", "#{client_tty}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
        return result.returncode == 0 and bool(result.stdout.strip())

    def check(self) -> TmuxResult:
        if self.path is None:
            return TmuxResult(False, "未安装 tmux，或 tmux 不在 PATH 中。")
        if self.has_attached_client():
            return TmuxResult(True, "已检测到本机 tmux 客户端，本地直连模式可用。")
        return TmuxResult(
            False,
            "未检测到已连接的本机 tmux 客户端；请先在本机终端进入 tmux 会话。",
        )
