#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt

pyinstaller --clean hshell.spec

APP_PATH="dist/Hshell.app"
DMG_PATH="dist/Hshell.dmg"

if [[ ! -d "$APP_PATH" ]]; then
  echo "❌ PyInstaller가 앱 번들을 생성하지 못했습니다." >&2
  exit 1
fi

hdiutil create -volname "Hshell" -srcfolder "$APP_PATH" -ov -format UDZO "$DMG_PATH"

echo "✅ 생성 완료"
echo "   - 앱 번들: $APP_PATH"
echo "   - DMG 파일: $DMG_PATH"

