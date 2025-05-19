# Hshell

SSH 터미널 및 포트 포워딩을 위한 GUI 도구입니다.

## 주요 기능

- SSH 서버 연결 관리
- 포트 포워딩 설정 및 관리
- 내장 터미널 에뮬레이터
- 서버 정보 암호화 저장

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
git clone https://github.com/yourusername/Hshell.git
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