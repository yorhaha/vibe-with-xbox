# 自定义配置

[← 返回 README](../README.md)

## 配置文件位置

创建并查看用户配置文件：

```bash
python xbox_vibe.py --init-config
python xbox_vibe.py --print-config-path
```

默认路径为：

```text
~/.config/vibe-with-xbox/config.json
```

也可以复制 [`config.example.json`](../config.example.json)，然后通过参数加载：

```bash
python xbox_vibe.py --config ./my-config.json
```

## 合并规则

配置会与内置默认值递归合并，因此只需要填写想覆盖的字段。修改完成后请退出并重新启动程序；当前版本不会在运行时自动重载配置。

查看配置合并后的实际映射：

```bash
python xbox_vibe.py --show-mapping
```

## 通用参数

常用参数位于 `general`：

| 字段 | 默认值 | 作用 |
| --- | --- | --- |
| `deadzone` | `0.5` | 左摇杆触发方向键的死区 |
| `trigger_threshold` | `0.2` | RT 被视为按下的阈值 |
| `repeat_initial_delay` | `0.35` | 左摇杆首次连发前的等待时间，单位为秒 |
| `repeat_rate` | `0.08` | 左摇杆持续拨动时的连发间隔，单位为秒 |
| `auto_start_bridge` | `false` | 启动程序后自动开始映射，无需点击 **启动手柄映射** |
| `show_action_toasts` | `true` | 在页面中显示最近一次操作的提示 |

## 按键映射

`buttons` 与 `stick` 两个字段存放每个手柄输入的映射定义，包含显示名称、描述和行为。默认值与结构可参考 [`config.example.json`](../config.example.json)；每个条目都带有 `enabled` 开关，设为 `false` 即可停用对应输入。

tmux 操作始终通过本机 `tmux` CLI 执行，只控制本机 tmux server，不支持 SSH 主机上的远端 tmux。操作时前台窗口无需保持在终端，但本机必须至少有一个已连接的 tmux 客户端。
