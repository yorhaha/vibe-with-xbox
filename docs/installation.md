# 安装与 macOS 设置

[← 返回 README](../README.md)

## 环境要求

- macOS 12 或更高版本。
- Python 3.10 或更高版本。
- 可通过蓝牙连接到 Mac 的 Xbox 手柄。
- 本机安装的 [tmux](https://github.com/tmux/tmux)，仅在使用窗格相关功能时需要。
- macOS 辅助功能权限，用于向其他应用发送按键。

## 1. 安装依赖

克隆或下载仓库后，在项目目录执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

如需使用 tmux 窗格操作，请在本机安装 tmux。例如使用 Homebrew：

```bash
brew install tmux
```

## 2. 完成 macOS 设置

1. 打开 **系统设置 → 蓝牙**，连接 Xbox 手柄。
2. 打开 **系统设置 → 隐私与安全性 → 辅助功能**，为运行本项目的 Terminal、Python，或打包后的 `Vibe with Xbox.app` 授权。
3. 如需窗格操作，在本机终端启动一个 tmux 会话：

   ```bash
   tmux new -A -s vibe
   ```

辅助功能权限需要在授权后完全退出并重新启动目标程序才会生效。如果授权后仍然无效，请参考[常见问题](troubleshooting.md)。

## 3. 运行环境自检

```bash
python xbox_vibe.py --doctor
```

自检会检查手柄连接、辅助功能权限和 tmux 是否可用。确认无误后，回到 [README](../README.md#快速开始) 启动程序，或继续阅读[使用说明](usage.md)。
