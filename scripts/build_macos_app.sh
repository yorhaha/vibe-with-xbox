#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m venv .venv-build
".venv-build/bin/python" -m pip install --upgrade pip
".venv-build/bin/python" -m pip install -r requirements-dev.txt
".venv-build/bin/pyinstaller" vibe-with-xbox.spec --clean --noconfirm

echo
echo "Built: $ROOT_DIR/dist/Vibe with Xbox.app"
echo "Tip: drag the app into /Applications, then grant Accessibility permission on first launch."
