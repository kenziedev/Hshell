# gui/main_window_v2.py
"""
피그마 디자인을 기반으로 완전히 새로 작성한 MainWindow
기존 기능 로직은 유지하되 UI 구조는 피그마를 그대로 복제
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QTextEdit, QLineEdit, QGridLayout, QSpacerItem, QSizePolicy,
    QDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor

from core.tunnel_config import load_server_list, save_server_list
from core.ssh_manager import SSHManager
from gui.icon_data import get_icon
from gui.theme import Theme
from gui.styled_message_box import StyledMessageBox
from gui.components.server_form_inline import ServerFormInline


class MainWindow(QMainWindow):
    """피그마 App.tsx를 그대로 복제한 메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        
        # 기능 관련 상태 변수
        self.ssh_managers = {}
        self.connected_indices = set()
        self.servers = []
        self.editing_server_index = None
        self.server_form = None  # 인라인 서버 폼
        
        # 윈도우 기본 설정
        self.setWindowTitle("Hshell")
        self.setWindowIcon(get_icon())
        self.setGeometry(100, 100, 1400, 900)
        
        # UI 초기화
        self.init_ui()
        
        # 데이터 로드
        self.servers = load_server_list()
        self.refresh_server_list()
        
        # 연결 상태 확인 타이머
        self.connection_check_timer = QTimer(self)
        self.connection_check_timer.timeout.connect(self.check_all_connections)
        self.connection_check_timer.start(5000)
    
    def init_ui(self):
        """피그마 디자인 기반 UI 구조 생성"""
        
        # Central Widget
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        
        # 메인 레이아웃 (세로)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ==================== 1. 상단 헤더 (slate-800) ====================
        self.create_header(main_layout)
        
        # ==================== 2. 메인 콘텐츠 영역 ====================
        content_area = QWidget()
        content_area.setObjectName("contentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(24, 24, 24, 16)
        content_layout.setSpacing(16)
        
        # 2-1. 메인 카드 (서버 관리)
        self.create_main_card(content_layout)
        
        # 2-2. 하단 제어 패널 (ConnectionStatus + 토글 버튼)
        self.create_bottom_controls(content_layout)
        
        # 2-3. 스크립트 패널 (토글 가능)
        self.create_script_panel(content_layout)
        
        # 2-4. 터미널 패널 (토글 가능)
        self.create_terminal_panel(content_layout)
        
        main_layout.addWidget(content_area, stretch=1)
        
        # 전역 스타일 적용
        self.setStyleSheet(self.get_main_stylesheet())
    
    def create_header(self, layout):
        """상단 헤더 바 생성 (피그마 기준)"""
        header = QFrame()
        header.setObjectName("headerBar")
        header.setFixedHeight(48)
        
        # 배경색 강제 설정
        header.setAutoFillBackground(True)
        palette = header.palette()
        palette.setColor(QPalette.Window, QColor(Theme.TITLEBAR_BG))
        header.setPalette(palette)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)
        header_layout.setSpacing(10)
        
        # 왼쪽: 아이콘 + 앱명
        icon_label = QLabel("🌐")
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("Hshell")
        title_label.setObjectName("headerTitle")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 오른쪽: 설정 버튼
        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("settingsBtn")
        settings_btn.setFixedSize(32, 32)
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(settings_btn)
        
        layout.addWidget(header)
    
    def create_main_card(self, layout):
        """메인 카드 - 서버 관리 영역"""
        card = QFrame()
        card.setObjectName("mainCard")
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        # 카드 헤더 (slate-50 배경)
        header = QWidget()
        header.setObjectName("cardHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(8)
        
        # 타이틀
        title = QLabel("SSH 서버 관리")
        title.setObjectName("cardTitle")
        header_layout.addWidget(title)
        
        # 서브타이틀
        subtitle = QLabel("SSH 터널과 서버 연결을 관리합니다")
        subtitle.setObjectName("cardSubtitle")
        header_layout.addWidget(subtitle)
        
        card_layout.addWidget(header)
        
        # 카드 바디 (스크롤 가능한 서버 리스트)
        body = QWidget()
        body.setObjectName("cardBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(24, 16, 24, 24)
        body_layout.setSpacing(12)
        
        # 서버 추가 버튼
        add_btn = QPushButton("+ 새 서버 추가")
        add_btn.setObjectName("addServerBtn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.show_add_form)
        body_layout.addWidget(add_btn)
        
        # 서버 리스트 컨테이너 (스크롤 영역)
        scroll = QScrollArea()
        scroll.setObjectName("serverScrollArea")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.server_container = QWidget()
        self.server_container.setObjectName("serverContainer")
        self.server_layout = QVBoxLayout(self.server_container)
        self.server_layout.setContentsMargins(0, 0, 0, 0)
        self.server_layout.setSpacing(12)
        self.server_layout.addStretch()
        
        scroll.setWidget(self.server_container)
        body_layout.addWidget(scroll, stretch=1)
        
        card_layout.addWidget(body, stretch=1)
        layout.addWidget(card, stretch=1)
    
    def create_bottom_controls(self, layout):
        """하단 제어 패널"""
        controls = QWidget()
        controls.setObjectName("bottomControls")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)
        
        # ConnectionStatus 카드
        self.connection_status = self.create_connection_status()
        controls_layout.addWidget(self.connection_status, stretch=1)
        
        # 스크립트 실행 토글 버튼
        self.script_btn = QPushButton("📄 스크립트 실행")
        self.script_btn.setObjectName("scriptToggleBtn")
        self.script_btn.setProperty("active", False)
        self.script_btn.setCursor(Qt.PointingHandCursor)
        self.script_btn.clicked.connect(self.toggle_script_panel)
        controls_layout.addWidget(self.script_btn)
        
        # 터미널 토글 버튼
        self.terminal_btn = QPushButton("💻 터미널")
        self.terminal_btn.setObjectName("terminalToggleBtn")
        self.terminal_btn.setProperty("active", False)
        self.terminal_btn.setCursor(Qt.PointingHandCursor)
        self.terminal_btn.clicked.connect(self.toggle_terminal_panel)
        controls_layout.addWidget(self.terminal_btn)
        
        layout.addWidget(controls)
    
    def create_connection_status(self):
        """ConnectionStatus 카드 생성"""
        status_card = QFrame()
        status_card.setObjectName("connectionStatus")
        
        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(16, 12, 16, 12)
        status_layout.setSpacing(16)
        
        # 아이콘
        icon = QLabel("🌐")
        icon.setFixedSize(24, 24)
        icon.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(icon)
        
        # 정보 영역
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        self.status_title = QLabel("네트워크 상태")
        self.status_title.setObjectName("statusTitle")
        info_layout.addWidget(self.status_title)
        
        self.status_detail = QLabel("활성 터널: 0개")
        self.status_detail.setObjectName("statusDetail")
        info_layout.addWidget(self.status_detail)
        
        status_layout.addLayout(info_layout, stretch=1)
        
        # 상태 배지
        self.status_badge = QLabel("실행 중")
        self.status_badge.setObjectName("statusBadge")
        status_layout.addWidget(self.status_badge)
        
        return status_card
    
    def create_script_panel(self, layout):
        """스크립트 실행 패널 (토글 가능)"""
        self.script_panel = QFrame()
        self.script_panel.setObjectName("scriptPanel")
        self.script_panel.setVisible(False)
        
        panel_layout = QVBoxLayout(self.script_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        # 헤더
        header = QWidget()
        header.setObjectName("panelHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        
        header_title = QLabel("📄 스크립트 실행")
        header_title.setObjectName("panelTitle")
        header_layout.addWidget(header_title)
        
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("panelCloseBtn")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.toggle_script_panel)
        header_layout.addWidget(close_btn)
        
        panel_layout.addWidget(header)
        
        # 바디
        body = QWidget()
        body.setObjectName("panelBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(16, 16, 16, 16)
        body_layout.setSpacing(12)
        
        # 스크립트 입력
        script_label = QLabel("실행할 명령어:")
        body_layout.addWidget(script_label)
        
        self.script_input = QLineEdit()
        self.script_input.setPlaceholderText("예: ls -la")
        body_layout.addWidget(self.script_input)
        
        # 실행 버튼
        run_btn = QPushButton("실행")
        run_btn.clicked.connect(self.run_script)
        body_layout.addWidget(run_btn)
        
        # 결과 출력
        result_label = QLabel("실행 결과:")
        body_layout.addWidget(result_label)
        
        self.script_output = QTextEdit()
        self.script_output.setReadOnly(True)
        self.script_output.setMaximumHeight(200)
        body_layout.addWidget(self.script_output, stretch=1)
        
        panel_layout.addWidget(body, stretch=1)
        layout.addWidget(self.script_panel)
    
    def create_terminal_panel(self, layout):
        """터미널 패널 (토글 가능)"""
        self.terminal_panel = QFrame()
        self.terminal_panel.setObjectName("terminalPanel")
        self.terminal_panel.setVisible(False)
        
        panel_layout = QVBoxLayout(self.terminal_panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)
        
        # 헤더
        header = QWidget()
        header.setObjectName("panelHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)
        
        header_title = QLabel("💻 터미널")
        header_title.setObjectName("panelTitle")
        header_layout.addWidget(header_title)
        
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("panelCloseBtn")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.toggle_terminal_panel)
        header_layout.addWidget(close_btn)
        
        panel_layout.addWidget(header)
        
        # 바디
        self.terminal_output = QTextEdit()
        self.terminal_output.setObjectName("terminalOutput")
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setMaximumHeight(300)
        self.terminal_output.setText("$ Hshell Terminal\n$ Ready...")
        
        panel_layout.addWidget(self.terminal_output, stretch=1)
        layout.addWidget(self.terminal_panel)
    
    # ========== UI 스타일 ==========
    
    def get_main_stylesheet(self):
        """메인 윈도우 스타일시트"""
        return f"""
            /* 전역 설정 */
            * {{
                font-family: {Theme.FONT_FAMILY};
            }}
            
            QMainWindow {{
                background-color: {Theme.BACKGROUND};
            }}
            
            #centralWidget {{
                background-color: {Theme.BACKGROUND};
            }}
            
            #contentArea {{
                background-color: {Theme.BACKGROUND};
            }}
            
            /* ========== 헤더 ========== */
            #headerBar {{
                background-color: {Theme.TITLEBAR_BG};
                border: none;
            }}
            
            #headerTitle {{
                font-size: 15px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.TITLEBAR_TEXT};
                background: transparent;
            }}
            
            #settingsBtn {{
                background: transparent;
                border: none;
                border-radius: 4px;
                color: {Theme.TITLEBAR_TEXT};
                font-size: 16px;
            }}
            
            #settingsBtn:hover {{
                background: {Theme.TITLEBAR_HOVER};
            }}
            
            /* ========== 메인 카드 ========== */
            #mainCard {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
            }}
            
            #cardHeader {{
                background-color: #f8fafc;
                border-bottom: 1px solid {Theme.BORDER_SOLID};
                border-top-left-radius: {Theme.RADIUS_LG};
                border-top-right-radius: {Theme.RADIUS_LG};
            }}
            
            #cardTitle {{
                font-size: {Theme.FONT_SIZE_XL};
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.FOREGROUND};
                background: transparent;
            }}
            
            #cardSubtitle {{
                font-size: {Theme.FONT_SIZE_SM};
                color: {Theme.MUTED_FOREGROUND};
                background: transparent;
            }}
            
            #cardBody {{
                background-color: {Theme.CARD};
            }}
            
            #addServerBtn {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_FOREGROUND};
                border: none;
                border-radius: {Theme.RADIUS_MD};
                padding: 10px 20px;
                font-size: {Theme.FONT_SIZE_BASE};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                min-height: 40px;
            }}
            
            #addServerBtn:hover {{
                background-color: #1a1a2e;
            }}
            
            #serverScrollArea {{
                background: transparent;
                border: none;
            }}
            
            #serverContainer {{
                background: transparent;
            }}
            
            /* ========== 하단 제어 패널 ========== */
            #connectionStatus {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
            }}
            
            #statusTitle {{
                font-size: {Theme.FONT_SIZE_SM};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                color: {Theme.FOREGROUND};
                background: transparent;
            }}
            
            #statusDetail {{
                font-size: {Theme.FONT_SIZE_SM};
                color: {Theme.MUTED_FOREGROUND};
                background: transparent;
            }}
            
            #statusBadge {{
                background-color: {Theme.STATUS_ACTIVE_BG};
                color: {Theme.STATUS_ACTIVE_TEXT};
                border: none;
                border-radius: {Theme.RADIUS_SM};
                padding: 4px 12px;
                font-size: {Theme.FONT_SIZE_SM};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            }}
            
            #scriptToggleBtn, #terminalToggleBtn {{
                background-color: {Theme.CARD};
                color: {Theme.FOREGROUND};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: 10px 20px;
                font-size: {Theme.FONT_SIZE_BASE};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                min-height: 40px;
            }}
            
            #scriptToggleBtn:hover, #terminalToggleBtn:hover {{
                background-color: {Theme.ACCENT};
                border: 1px solid {Theme.PRIMARY};
            }}
            
            #scriptToggleBtn[active="true"], #terminalToggleBtn[active="true"] {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_FOREGROUND};
                border: 1px solid {Theme.PRIMARY};
            }}
            
            /* ========== 토글 패널 ========== */
            #scriptPanel, #terminalPanel {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
            }}
            
            #panelHeader {{
                background-color: #1e293b;
                border-top-left-radius: {Theme.RADIUS_LG};
                border-top-right-radius: {Theme.RADIUS_LG};
            }}
            
            #panelTitle {{
                font-size: {Theme.FONT_SIZE_BASE};
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: #ffffff;
                background: transparent;
            }}
            
            #panelCloseBtn {{
                background: transparent;
                border: none;
                color: #ffffff;
                font-size: 14px;
            }}
            
            #panelCloseBtn:hover {{
                background: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }}
            
            #panelBody {{
                background-color: {Theme.CARD};
            }}
            
            #terminalOutput {{
                background-color: #0f172a;
                color: #10b981;
                border: none;
                border-bottom-left-radius: {Theme.RADIUS_LG};
                border-bottom-right-radius: {Theme.RADIUS_LG};
                padding: 16px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: {Theme.FONT_SIZE_SM};
            }}
            
            /* ========== 입력 필드 (전역) ========== */
            QLineEdit {{
                background-color: {Theme.INPUT_BACKGROUND};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: 8px 12px;
                color: {Theme.FOREGROUND};
                font-size: {Theme.FONT_SIZE_BASE};
                min-height: 36px;
            }}
            
            QLineEdit:focus {{
                border: 1px solid {Theme.PRIMARY};
                background-color: {Theme.CARD};
            }}
            
            QLineEdit:hover {{
                border: 1px solid {Theme.PRIMARY};
            }}
            
            /* ========== 버튼 (전역) ========== */
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_FOREGROUND};
                border: none;
                border-radius: {Theme.RADIUS_MD};
                padding: 8px 16px;
                font-size: {Theme.FONT_SIZE_SM};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                min-height: 36px;
            }}
            
            QPushButton:hover {{
                background-color: #1a1a2e;
            }}
            
            QPushButton[buttonStyle="outline"] {{
                background-color: transparent;
                color: {Theme.FOREGROUND};
                border: 1px solid {Theme.BORDER_SOLID};
            }}
            
            QPushButton[buttonStyle="outline"]:hover {{
                background-color: {Theme.ACCENT};
            }}
            
            QPushButton[buttonStyle="destructive"] {{
                background-color: {Theme.DESTRUCTIVE};
                color: {Theme.DESTRUCTIVE_FOREGROUND};
            }}
            
            QPushButton[buttonStyle="destructive"]:hover {{
                background-color: #b81636;
            }}
            
            /* ========== 인라인 서버 폼 ========== */
            #tunnelDeleteBtn {{
                background: transparent;
                border: none;
                color: {Theme.DESTRUCTIVE};
                font-size: 14px;
                border-radius: 4px;
            }}
            
            #tunnelDeleteBtn:hover {{
                background: rgba(212, 24, 61, 0.1);
            }}
        """
    
    # ========== 이벤트 핸들러 (기존 로직 유지) ==========
    
    def show_add_form(self):
        """서버 추가 폼 표시 (인라인)"""
        if self.server_form:
            # 이미 폼이 열려있으면 닫기
            self.close_server_form()
            return
        
        self.server_form = ServerFormInline(parent=self)
        self.server_form.save_clicked.connect(self.on_server_form_save)
        self.server_form.cancel_clicked.connect(self.close_server_form)
        
        # 서버 리스트 맨 위에 폼 추가
        self.server_layout.insertWidget(0, self.server_form)
    
    def toggle_script_panel(self):
        """스크립트 패널 토글"""
        is_visible = self.script_panel.isVisible()
        self.script_panel.setVisible(not is_visible)
        self.script_btn.setProperty("active", not is_visible)
        self.script_btn.style().unpolish(self.script_btn)
        self.script_btn.style().polish(self.script_btn)
        
        if not is_visible and self.terminal_panel.isVisible():
            self.terminal_panel.setVisible(False)
            self.terminal_btn.setProperty("active", False)
            self.terminal_btn.style().unpolish(self.terminal_btn)
            self.terminal_btn.style().polish(self.terminal_btn)
    
    def toggle_terminal_panel(self):
        """터미널 패널 토글"""
        is_visible = self.terminal_panel.isVisible()
        self.terminal_panel.setVisible(not is_visible)
        self.terminal_btn.setProperty("active", not is_visible)
        self.terminal_btn.style().unpolish(self.terminal_btn)
        self.terminal_btn.style().polish(self.terminal_btn)
        
        if not is_visible and self.script_panel.isVisible():
            self.script_panel.setVisible(False)
            self.script_btn.setProperty("active", False)
            self.script_btn.style().unpolish(self.script_btn)
            self.script_btn.style().polish(self.script_btn)
    
    def run_script(self):
        """스크립트 실행"""
        command = self.script_input.text().strip()
        if not command:
            self.script_output.append("[오류] 명령어를 입력하세요.")
            return
        
        self.script_output.append(f"\n$ {command}")
        self.script_output.append("[정보] 스크립트 실행 기능 (미구현)")
    
    def refresh_server_list(self):
        """서버 리스트 새로고침"""
        # 기존 서버 카드 제거
        while self.server_layout.count() > 1:  # stretch 제외
            item = self.server_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 서버 카드 생성
        for idx, server in enumerate(self.servers):
            is_connected = idx in self.connected_indices
            card = self.create_server_card(idx, server, is_connected)
            self.server_layout.insertWidget(self.server_layout.count() - 1, card)
        
        # ConnectionStatus 업데이트
        self.update_connection_status()
    
    def create_server_card(self, index, server, is_connected):
        """서버 카드 생성"""
        card = QFrame()
        card.setObjectName("serverCard")
        card.setStyleSheet(f"""
            QFrame#serverCard {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
                padding: 20px;
            }}
            QFrame#serverCard:hover {{
                border: 1px solid {Theme.PRIMARY};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        
        # 헤더: 서버명 + 상태
        header_layout = QHBoxLayout()
        
        name_label = QLabel(server['name'])
        name_label.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_LG};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
        """)
        header_layout.addWidget(name_label)
        
        status_badge = QLabel("연결됨" if is_connected else "연결 안됨")
        status_badge.setStyleSheet(f"""
            background-color: {Theme.STATUS_ACTIVE_BG if is_connected else Theme.STATUS_INACTIVE_BG};
            color: {Theme.STATUS_ACTIVE_TEXT if is_connected else Theme.STATUS_INACTIVE_TEXT};
            border: none;
            border-radius: {Theme.RADIUS_SM};
            padding: 4px 12px;
            font-size: {Theme.FONT_SIZE_SM};
            font-weight: {Theme.FONT_WEIGHT_MEDIUM};
        """)
        header_layout.addWidget(status_badge)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # 서버 정보
        info_label = QLabel(f"{server['username']}@{server['host']}:{server['port']}")
        info_label.setStyleSheet(f"""
            color: {Theme.MUTED_FOREGROUND};
            font-size: {Theme.FONT_SIZE_SM};
        """)
        layout.addWidget(info_label)
        
        # 터널 정보
        if server.get('tunnels'):
            tunnel_label = QLabel(f"{len(server['tunnels'])}개 터널")
            tunnel_label.setStyleSheet(f"""
                background-color: {Theme.SECONDARY};
                color: {Theme.FOREGROUND};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_SM};
                padding: 2px 8px;
                font-size: {Theme.FONT_SIZE_SM};
            """)
            layout.addWidget(tunnel_label, alignment=Qt.AlignLeft)
        
        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {Theme.BORDER_SOLID}; max-height: 1px;")
        layout.addWidget(separator)
        
        # 버튼들
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        if is_connected:
            stop_btn = QPushButton("⏹ 중지")
            stop_btn.setProperty("buttonStyle", "outline")
            stop_btn.clicked.connect(lambda: self.disconnect_server(index))
            button_layout.addWidget(stop_btn)
            
            ssh_btn = QPushButton("SSH")
            ssh_btn.clicked.connect(lambda: self.open_ssh_console(index))
            button_layout.addWidget(ssh_btn)
        else:
            start_btn = QPushButton("▶ 시작")
            start_btn.clicked.connect(lambda: self.connect_server(index))
            button_layout.addWidget(start_btn)
        
        button_layout.addStretch()
        
        edit_btn = QPushButton("✏ 수정")
        edit_btn.setProperty("buttonStyle", "outline")
        edit_btn.clicked.connect(lambda: self.edit_server(index))
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑 삭제")
        delete_btn.setProperty("buttonStyle", "destructive")
        delete_btn.clicked.connect(lambda: self.delete_server(index))
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        return card
    
    def update_connection_status(self):
        """ConnectionStatus 업데이트"""
        connected_count = len(self.connected_indices)
        total_tunnels = sum(len(s.get('tunnels', [])) for s in self.servers)
        
        self.status_detail.setText(f"활성 터널: {connected_count}개 | 총 {total_tunnels}개 터널")
    
    def connect_server(self, index):
        """서버 연결"""
        self.terminal_output.append(f"\n[연결] {self.servers[index]['name']} 연결 시도...")
        try:
            server = self.servers[index]
            ssh_manager = SSHManager(
                server['host'],
                server['port'],
                server['username'],
                server.get('password', ''),
                server.get('key_path', '')
            )
            
            if ssh_manager.connect():
                self.ssh_managers[index] = ssh_manager
                self.connected_indices.add(index)
                
                # 터널 설정
                for tunnel in server.get('tunnels', []):
                    ssh_manager.create_tunnel(
                        tunnel['local'],
                        tunnel['remote_host'],
                        tunnel['remote_port']
                    )
                
                self.terminal_output.append(f"[성공] {server['name']} 연결 완료!")
                self.refresh_server_list()
            else:
                self.terminal_output.append(f"[오류] {server['name']} 연결 실패")
        except Exception as e:
            self.terminal_output.append(f"[오류] {str(e)}")
    
    def disconnect_server(self, index):
        """서버 연결 해제"""
        if index in self.ssh_managers:
            self.ssh_managers[index].disconnect()
            del self.ssh_managers[index]
            self.connected_indices.remove(index)
            self.terminal_output.append(f"\n[연결 종료] {self.servers[index]['name']}")
            self.refresh_server_list()
    
    def edit_server(self, index):
        """서버 수정 (인라인)"""
        if self.server_form:
            # 이미 폼이 열려있으면 닫기
            self.close_server_form()
        
        self.editing_server_index = index
        self.server_form = ServerFormInline(server_data=self.servers[index], parent=self)
        self.server_form.save_clicked.connect(self.on_server_form_save)
        self.server_form.cancel_clicked.connect(self.close_server_form)
        
        # 서버 리스트 맨 위에 폼 추가
        self.server_layout.insertWidget(0, self.server_form)
    
    def on_server_form_save(self, result):
        """서버 폼 저장 처리"""
        if self.editing_server_index is not None:
            # 수정
            index = self.editing_server_index
            if index in self.connected_indices:
                self.disconnect_server(index)
            
            self.servers[index] = result
            self.terminal_output.append(f"\n[성공] {result['name']} 서버 정보가 수정되었습니다.")
            self.editing_server_index = None
        else:
            # 추가
            self.servers.append(result)
            self.terminal_output.append(f"\n[성공] {result['name']} 서버가 추가되었습니다.")
        
        save_server_list(self.servers)
        self.close_server_form()
        self.refresh_server_list()
    
    def close_server_form(self):
        """서버 폼 닫기"""
        if self.server_form:
            self.server_layout.removeWidget(self.server_form)
            self.server_form.deleteLater()
            self.server_form = None
            self.editing_server_index = None
    
    def delete_server(self, index):
        """서버 삭제"""
        reply = QMessageBox.question(
            self, '삭제 확인',
            f"{self.servers[index]['name']} 서버를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if index in self.connected_indices:
                self.disconnect_server(index)
            
            del self.servers[index]
            save_server_list(self.servers)
            self.terminal_output.append(f"\n[삭제] 서버가 삭제되었습니다.")
            self.refresh_server_list()
    
    def open_ssh_console(self, index):
        """SSH 콘솔 열기"""
        self.terminal_output.append(f"\n[SSH] {self.servers[index]['name']} SSH 콘솔 (미구현)")
        if not self.terminal_panel.isVisible():
            self.toggle_terminal_panel()
    
    def check_all_connections(self):
        """모든 연결 상태 확인"""
        disconnected = set()
        for index in list(self.connected_indices):
            if index in self.ssh_managers:
                if not self.ssh_managers[index].is_connected():
                    disconnected.add(index)
                    self.terminal_output.append(f"\n[경고] {self.servers[index]['name']} 연결 끊김")
        
        for index in disconnected:
            if index in self.ssh_managers:
                self.ssh_managers[index].disconnect()
                del self.ssh_managers[index]
            self.connected_indices.remove(index)
        
        if disconnected:
            self.refresh_server_list()
    
    def show_settings(self):
        """설정 다이얼로그"""
        self.terminal_output.append("\n[정보] 설정 기능 (미구현)")

