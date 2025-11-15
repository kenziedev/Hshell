# Hshell

🌐 SSH 터미널 및 포트 포워딩을 위한 모던한 GUI 도구입니다.

## 주요 기능

- 🔐 SSH 서버 연결 관리
- 🔗 포트 포워딩 설정 및 관리
- 💻 내장 터미널 에뮬레이터
- 🔒 서버 정보 암호화 저장
- 🎨 **Figma 디자인 시스템 기반 모던 UI**
  - shadcn/ui 스타일의 일관된 컴포넌트
  - TailwindCSS 색상 팔레트 적용
  - 직관적이고 깔끔한 사용자 경험
- 📊 실시간 연결 상태 모니터링
- ⚡ 빠르고 반응성 있는 사용자 인터페이스

## 설치 방법

### pip를 통한 설치

```bash
pip install -r requirements.txt
```

### 실행 파일 다운로드

[릴리즈 페이지](https://github.com/kenziedev/Hshell/releases)에서 최신 버전의 실행 파일을 다운로드할 수 있습니다.

## 개발 환경 설정

1. 저장소 클론
```bash
git clone https://github.com/kenziedev/Hshell.git
cd Hshell
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 의존성 설치
```bash
pip install -r requirements.txt
```

4. 개발 모드로 실행
```bash
python main.py
```

## 빌드 방법

PyInstaller를 사용하여 실행 파일을 빌드할 수 있습니다:

```bash
python -m PyInstaller hshell.spec
```

빌드된 파일은 `dist` 디렉토리에 생성됩니다.

### macOS 설치 파일 생성

1. (선택) `image/hshell.icns` 아이콘 준비  
   - macOS에서는 `.icns` 포맷을 사용합니다. 아이콘이 없다면 아래와 같이 PNG들을 `.iconset`으로 만든 뒤 `iconutil`을 이용해 변환할 수 있습니다.  
   ```bash
   mkdir -p image/Hshell.iconset
   sips -z 16 16   image/hshell.png --out image/Hshell.iconset/icon_16x16.png
   # ...필요한 해상도 추가...
   iconutil -c icns image/Hshell.iconset -o image/hshell.icns
   ```
   - `.icns`가 없으면 기존 `.ico`가 그대로 사용됩니다.
2. 스크립트 실행  
   ```bash
   chmod +x scripts/build_macos.sh
   ./scripts/build_macos.sh
   ```
3. 결과물 확인  
   - `dist/Hshell.app`: 더블클릭 가능한 앱 번들  
   - `dist/Hshell.dmg`: 배포용 디스크 이미지
4. (선택) 코드 서명 & 공증  
   ```bash
   codesign --deep --force --sign "Developer ID Application: YOUR NAME" dist/Hshell.app
   xcrun notarytool submit dist/Hshell.dmg --wait --apple-id you@example.com --team-id TEAMID --password "app-specific-password"
   ```

## 사용 방법

1. 프로그램 실행
2. "서버 추가" 버튼을 클릭하여 새로운 서버 정보 입력
3. 서버 선택 후 "ON" 버튼으로 연결
4. "SSH" 버튼으로 터미널 접속
5. "포트포워딩 추가"로 터널링 설정

## 라이선스

MIT License

## 기여 방법

1. 이슈 생성 또는 기존 이슈 확인
2. 브랜치 생성 (`feature/기능명` 또는 `fix/버그명`)
3. 변경사항 커밋
4. Pull Request 생성

## 보안 관련

- 서버 비밀번호는 암호화되어 저장됩니다.
- SSH 키 기반 인증을 지원합니다.
- 모든 통신은 SSH 프로토콜을 통해 암호화됩니다. 
