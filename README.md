# Vibe with Xbox

**简体中文** | [English](README_EN.md)

把 Xbox 手柄变成 macOS 上的轻量遥控器，用来操作 **Claude Code** 和 **tmux**。

Vibe with Xbox 会在本机浏览器中打开按键说明与运行状态页面。连接手柄并启动映射后，可以用手柄确认或取消 Claude Code 提示、上下选择选项、按住右 Option 修饰键，以及管理 tmux 窗格。

> 当前版本：`0.2.0`。目前仅支持 macOS。

## 功能

- 浏览器页面显示手柄示意图、当前映射、连接状态和最近一次操作，按下实体按键时实时高亮。
- 页面提供运行环境检查、打开配置文件、跳转辅助功能设置和退出应用等操作。
- 向当前获得焦点的 macOS 应用发送 `Enter`、`Esc`、方向键和右 `Option` 修饰键。
- 通过十字键、右摇杆、LB、RB 和 RT 管理本机 tmux 窗格与会话，直接调用 `tmux` CLI，不依赖前台窗口焦点。
- 单击 Start，将预设的 commit、push 与温和重启指令输入当前应用。
- 提供环境检查、原始手柄事件调试、自定义 JSON 配置和无界面运行模式。
- 本地页面仅监听 `127.0.0.1`；项目代码不会把按键事件发送到云端。

## 默认映射

| 手柄输入 | 默认操作 |
| --- | --- |
| A | `Enter` |
| B | `Esc` |
| 按住 X | 按住 macOS 右 `Option` |
| Y | `↓` + `Enter` |
| 左摇杆上 / 下 | `↑` / `↓`（持续拨动自动重复） |
| 右摇杆上 / 下 / 左 / 右 | 切换到对应方向的 tmux 窗格 |
| 十字键上 / 下 / 左 / 右 | 新建对应方向的 tmux 窗格 |
| LB / RB | 上一个 / 下一个 tmux session |
| 长按 RT 0.7 秒 | 关闭当前 tmux 窗格 |
| Start | 输入重启指令（不自动按 Enter） |

LT、摇杆按下、View、Share、Xbox 键，以及左摇杆的左右方向暂未映射。每个按键的行为细节见[按键映射](docs/controller-mapping.md)。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

python xbox_vibe.py --doctor   # 环境自检
python xbox_vibe.py            # 启动
```

启动前请确认手柄已在 **系统设置 → 蓝牙** 中连接，并在 **系统设置 → 隐私与安全性 → 辅助功能** 中为 Terminal 或 Python 授权。使用 tmux 窗格功能还需要本机安装 tmux，并在终端中启动一个 tmux 会话。

程序会在默认浏览器中打开 `http://127.0.0.1:8765/`（端口被占用时自动改用其他本地端口）。页面加载时会自动运行一次环境检查，确认「手柄」等检查项正常后，点击 **启动手柄映射**，再切换到目标应用并保持其获得焦点。操作结束后，可在页面中点击 **停止** 结束映射，或点击 **退出应用** 关闭程序。

> 映射发送的是系统级按键，动作会作用于当前获得焦点的应用。开始操作前，请先确认焦点位于正确窗口。

完整的安装与 macOS 设置步骤见[安装与设置](docs/installation.md)。

## 文档

| 文档 | 内容 |
| --- | --- |
| [安装与 macOS 设置](docs/installation.md) | 环境要求、依赖安装、蓝牙与辅助功能授权、环境自检 |
| [使用说明](docs/usage.md) | 启动流程、页面操作、无界面模式与命令行参数 |
| [按键映射](docs/controller-mapping.md) | 完整键位表与每个按键的行为细节 |
| [自定义配置](docs/configuration.md) | 配置文件位置、合并规则与可调参数 |
| [常见问题](docs/troubleshooting.md) | 手柄、按键、Option、tmux 与页面的排查步骤 |
| [构建 macOS App](docs/build-macos-app.md) | PyInstaller 打包与签名说明 |
| [参与开发](docs/development.md) | 项目结构、测试与贡献流程 |

## 许可证

本项目采用 [MIT License](LICENSE)。
