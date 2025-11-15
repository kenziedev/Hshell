# Figma 디자인 적용 변경 사항

## 개요

Hshell 애플리케이션의 UI를 [Figma Make 디자인](https://www.figma.com/make/UGQZjBCdgewZXiz3pXMxNP/Hshell-디자인--Community-?node-id=0-1)에 맞춰 전면 개편했습니다.

피그마 디자인 시스템(shadcn/ui 스타일)을 PyQt5로 정확하게 구현하여 일관되고 모던한 사용자 경험을 제공합니다.

## 주요 변경 사항

### 1. 색상 시스템 개선 (`gui/theme.py`)

**변경 전:**
- 기본 배경색: `#f8f9fa`
- 불일치하는 색상 팔레트

**변경 후:**
- 피그마 globals.css 기반 색상 시스템
- TailwindCSS 색상 팔레트 (slate, green, gray)
- 배경색: `#f1f5f9` (slate-100)
- 일관된 상태 색상 (Active, Inactive)

### 2. 버튼 스타일 통일

피그마의 Button variants 적용:
- **default**: Primary 버튼
- **outline**: 테두리 버튼 (보조 액션)
- **secondary**: Secondary 색상
- **ghost**: 투명 버튼 (최소 강조)
- **destructive**: 위험 동작

모든 버튼에 hover/pressed 상태 애니메이션 추가

### 3. 입력 필드 개선

피그마 Input 컴포넌트 스타일:
- 포커스 시 Primary 테두리 + 3px outline
- 일관된 패딩 및 border radius
- Placeholder 색상 개선
- Selection 스타일 추가

### 4. 서버 카드 재디자인 (`gui/components/server_card.py`)

**개선 사항:**
- 패딩 증가 (24px, 20px)
- 상태 배지: 연결됨(Green) / 연결 안됨(Gray)
- 터널 수를 Badge 스타일로 표시
- 버튼 아이콘 추가 (▶ 시작, ⏹ 중지, ✏ 수정, 🗑 삭제)
- 호버 효과: Primary 테두리 + 그림자

### 5. 서버 폼 카드 개선 (`gui/components/server_form_card.py`)

**개선 사항:**
- Primary 테두리 (2px)로 폼 강조
- 섹션 타이틀 크기 증가 및 아이콘 추가
- 터널 입력 행: Slate-50 배경 + 테두리
- 버튼 크기 및 패딩 증가 (40px 높이)
- 저장/취소 버튼에 체크 마크 아이콘 추가

### 6. 메인 윈도우 레이아웃 (`gui/main_window.py`)

**개선 사항:**
- 헤더 텍스트: "연결 서버 목록"
- 버튼: "+ 새 서버 추가"
- 스크롤바 스타일 개선 (8px 너비, 둥근 모서리)
- 로그 영역: 터미널 스타일 (어두운 배경, 녹색 텍스트)
- 카드 패딩 통일 (24px, 20px)

### 7. ConnectionStatus 재구성 (`gui/components/bottom_panel.py`)

피그마 ConnectionStatus.tsx 구현:
- 카드 스타일 배경
- 네트워크 상태 + 활성 터널 수 + 실행 중 배지
- 마지막 업데이트 시간 표시
- 아이콘 및 텍스트 배치 개선

### 8. 탭 위젯 스타일링

피그마 Tabs 컴포넌트 적용:
- 선택된 탭: 카드 배경 + 테두리
- 비선택 탭: 투명 배경
- 호버 효과 추가

## 새로 추가된 파일

1. **DESIGN_SYSTEM.md**
   - 전체 디자인 시스템 문서
   - 색상, 타이포그래피, 컴포넌트 가이드
   - 피그마-PyQt5 매핑 테이블

2. **CHANGELOG_FIGMA_DESIGN.md** (이 파일)
   - 피그마 디자인 적용 변경 사항 상세 기록

## 기술적 개선

### 스타일시트 최적화
- 전역 QSS 스타일시트 개선
- 컴포넌트별 스타일 분리
- CSS 변수 패턴 적용 (Theme 클래스 상수)

### 일관성 강화
- 모든 컴포넌트에 동일한 간격 시스템 적용
- Border radius 통일
- 색상 팔레트 통일

### 사용자 경험
- 호버/포커스 상태 명확화
- 버튼 아이콘으로 직관성 향상
- 상태 표시 개선 (배지, 아이콘)

## 테스트 완료 항목

✅ 색상 시스템 적용
✅ 버튼 variants 동작 확인
✅ 입력 필드 포커스 상태
✅ 서버 카드 호버 효과
✅ 폼 레이아웃 및 스타일
✅ ConnectionStatus 표시
✅ 전체 레이아웃 반응성
✅ Linter 오류 없음

## 다음 단계

- [ ] 다크 모드 지원 추가 (피그마 dark theme 활용)
- [ ] 애니메이션 추가 (카드 등장, 패널 토글)
- [ ] 접근성 개선 (키보드 내비게이션)
- [ ] 커스텀 아이콘 세트 적용

## 참고

- 피그마 디자인: https://www.figma.com/make/UGQZjBCdgewZXiz3pXMxNP/Hshell-디자인--Community-?node-id=0-1
- MCP를 통해 피그마 디자인 파일 직접 연동
- shadcn/ui 디자인 시스템 참고: https://ui.shadcn.com/

