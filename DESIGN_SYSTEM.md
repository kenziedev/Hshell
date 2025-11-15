# Hshell 디자인 시스템

이 문서는 Hshell의 UI 디자인 시스템을 설명합니다. 피그마의 [Hshell 디자인](https://www.figma.com/make/UGQZjBCdgewZXiz3pXMxNP/Hshell-디자인--Community-?node-id=0-1)을 기반으로 구축되었습니다.

## 색상 팔레트

### 기본 색상
- **Background**: `#f1f5f9` (slate-100) - 앱의 전체 배경색
- **Foreground**: `#0a0a0a` - 기본 텍스트 색상
- **Card**: `#ffffff` - 카드 배경색
- **Primary**: `#030213` - 주요 버튼, 강조 요소
- **Primary Foreground**: `#ffffff` - Primary 위의 텍스트

### 상태 색상
- **Muted**: `#ececf0` - 비활성화된 배경
- **Muted Foreground**: `#717182` - 보조 텍스트
- **Destructive**: `#d4183d` - 삭제, 위험 동작
- **Border**: `#e2e8f0` (slate-200) - 테두리

### 타이틀바
- **Titlebar BG**: `#1e293b` (slate-800)
- **Titlebar Hover**: `#334155` (slate-700)

### 상태 배지
- **Active BG**: `#dcfce7` (green-100)
- **Active Text**: `#166534` (green-800)
- **Inactive BG**: `#f3f4f6` (gray-100)
- **Inactive Text**: `#6b7280` (gray-500)

## 타이포그래피

### 폰트
- **Font Family**: `Segoe UI, Noto Sans KR, sans-serif`
- **Base Size**: `14px`
- **Small**: `13px`
- **Large**: `16px`
- **XL**: `18px`
- **2XL**: `22px`

### 폰트 굵기
- **Normal**: `400`
- **Medium**: `500`
- **Semibold**: `600`

## 간격 및 크기

### Border Radius
- **SM**: `6px`
- **MD**: `8px`
- **LG**: `10px`
- **XL**: `14px`

### Spacing
- **XS**: `4px`
- **SM**: `8px`
- **MD**: `12px`
- **LG**: `16px`
- **XL**: `24px`
- **2XL**: `32px`

## 컴포넌트

### 버튼 (Button)

피그마의 `components/ui/button.tsx` 기반

**Variants:**
- `default` - Primary 색상, 주요 액션
- `outline` - 투명 배경, 테두리만, 보조 액션
- `secondary` - Secondary 색상
- `ghost` - 완전히 투명, 최소한의 강조
- `destructive` - 위험한 동작 (삭제 등)

**Size:**
- `default` - 36px 높이
- `sm` - 32px 높이
- `lg` - 40px 높이

### 입력 필드 (Input)

피그마의 `components/ui/input.tsx` 기반

- 배경: `INPUT_BACKGROUND` (#f3f3f5)
- 포커스 시: Primary 테두리 + 3px 아웃라인
- 최소 높이: 36px
- Border Radius: MD (8px)

### 카드 (Card)

피그마의 `components/ui/card.tsx` 기반

- 배경: `CARD` (#ffffff)
- 테두리: 1px solid `BORDER_SOLID`
- Border Radius: LG (10px)
- 패딩: 24px (CardContent)
- 호버 시: Primary 테두리 + 그림자

### 배지 (Badge)

피그마의 `components/ui/badge.tsx` 기반

**연결 상태:**
- **연결됨**: Green-100 배경, Green-800 텍스트
- **연결 안됨**: Gray-100 배경, Gray-500 텍스트

**터널 수:**
- Outline variant
- Border Radius: SM (6px)

## 레이아웃

### MainWindow
- 상단: HeaderBar (48px 고정)
- 콘텐츠: 2열 레이아웃 (5:7 비율)
  - 왼쪽: 서버 카드 목록 (스크롤 가능)
  - 오른쪽: 터미널 탭 + 로그
- 하단: BottomPanel (ConnectionStatus + 토글 버튼)

### ServerCard
- 헤더: 서버명 + 상태 배지
- 본문: 서버 정보 (username@host:port)
- 터널: Badge 형태로 터널 수 표시
- 푸터: 액션 버튼들 (시작/중지, SSH, 수정, 삭제)

### ServerFormCard
- Primary 테두리 (2px)로 강조
- 섹션별 구분 (서버 정보 / 터널링 정보)
- 그리드 레이아웃 (2열)
- 터널 행: Slate-50 배경 카드

### ConnectionStatus
피그마의 `components/ConnectionStatus.tsx` 기반
- 카드 스타일 (배경, 테두리, 패딩)
- 네트워크 상태 + 활성 터널 수 + 실행 중 배지 + 마지막 업데이트 시간
- 아이콘 + 텍스트 레이아웃

## 피그마 매핑

| 피그마 컴포넌트 | PyQt5 위젯 | 파일 위치 |
|-----------------|-----------|----------|
| App.tsx | MainWindow | gui/main_window.py |
| TunnelManager.tsx | ServerCard + ServerFormCard | gui/components/ |
| ConnectionStatus.tsx | ConnectionStatus | gui/components/bottom_panel.py |
| Button | QPushButton + buttonStyle 속성 | gui/theme.py |
| Input | QLineEdit | gui/theme.py |
| Card | QFrame[frameStyle="card"] | gui/theme.py |
| Badge | QLabel + 스타일 | 컴포넌트별 구현 |

## 개발 가이드라인

1. **색상**: `Theme` 클래스의 상수 사용
2. **간격**: `Theme.SPACING_*` 사용
3. **Border Radius**: `Theme.RADIUS_*` 사용
4. **버튼**: `setProperty("buttonStyle", "variant")` 설정
5. **일관성**: 모든 컴포넌트는 피그마 디자인과 동일한 스타일 유지

## 참고 자료

- [Figma 디자인 파일](https://www.figma.com/make/UGQZjBCdgewZXiz3pXMxNP/Hshell-디자인--Community-?node-id=0-1)
- [shadcn/ui](https://ui.shadcn.com/) - 디자인 시스템 참고
- [TailwindCSS Colors](https://tailwindcss.com/docs/customizing-colors) - 색상 팔레트 참고

