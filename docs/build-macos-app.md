# 构建 macOS App

[← 返回 README](../README.md)

构建脚本会创建独立的 `.venv-build` 环境、安装开发依赖并运行 PyInstaller：

```bash
./scripts/build_macos_app.sh
```

输出位置：

```text
dist/Vibe with Xbox.app
```

把应用拖到 `/Applications` 后启动，并为它授予辅助功能权限。

> 当前脚本生成的是本地未签名构建。如果要向其他用户分发 `.app`，还需要自行完成 Developer ID 签名和 Apple 公证。
