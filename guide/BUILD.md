# macOS 빌드 가이드

Figma 디자인을 반영한 최신 UI가 포함된 `Hshell` 앱을 직접 빌드하려면 아래 순서를 따르면 됩니다.

## 1. 사전 준비
- macOS (Apple Silicon 또는 Intel)
- Python 3.12 이상이 `PATH`에 있어야 합니다.
- 처음 빌드하는 경우, 프로젝트 루트에 있는 `.venv`가 없으면 스크립트가 자동으로 생성합니다.

## 2. 빌드 명령어
프로젝트 루트(`/Users/hyunsikoh/Desktop/application/Hshell`)에서 다음 명령어 하나만 실행하면 됩니다.

```bash
./scripts/build_macos.sh
```

스크립트가 내부적으로 수행하는 작업:
1. `.venv` 가 없으면 생성 후 활성화
2. `requirements.txt` 설치
3. `pyinstaller --clean hshell.spec` 실행
4. `dist/Hshell.app` 과 `dist/Hshell.dmg` 생성

## 3. 결과물
- `dist/Hshell.app`: 실행 가능한 앱 번들
- `dist/Hshell.dmg`: 배포용 디스크 이미지

앱을 바로 실행하려면:

```bash
open dist/Hshell.app
```

## 4. 문제가 생길 때
- 이전 빌드 산출물이 꼬였을 때는 `rm -rf dist build` 후 다시 실행합니다.
- `permission denied` 오류가 나면, `./scripts/build_macos.sh` 앞에 `chmod +x scripts/build_macos.sh` 를 한 번 실행합니다.
- PyInstaller 가 `sip` 경고를 내지만 현재 동작에는 영향 없습니다.

이 가이드를 따라 실행하면 언제든지 동일한 UI/기능을 가진 macOS 앱 번들을 재생성할 수 있습니다.

