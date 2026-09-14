# 参与开发

[← 返回 README](../README.md)

## 项目结构

```text
vibe_with_xbox/
├── bridge.py        # pygame 手柄事件循环与动作分发
├── cli.py           # 命令行入口
├── config.py        # 默认映射与配置合并
├── doctor.py        # 环境检查
├── macos.py         # macOS 按键发送与辅助功能检查
├── tmux_control.py  # 本地 tmux 命令
└── ui.py            # 本地 HTTP 页面与实时事件
```

`xbox_vibe.py` 是启动入口，`tests/` 存放单元测试，`docs/` 存放文档。

## 开发环境

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

## 测试

```bash
python -m unittest discover -s tests
```

提交前建议至少运行：

```bash
python -m compileall vibe_with_xbox xbox_vibe.py
python -m unittest discover -s tests
python xbox_vibe.py --help
python xbox_vibe.py --show-mapping
```

## 提交 Pull Request

欢迎提交 Issue 和 Pull Request。

涉及实体手柄映射的修改，请同时使用 `--debug` 在 macOS 上验证，并更新[按键映射](controller-mapping.md)中的映射表。
