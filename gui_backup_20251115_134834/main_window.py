# gui/main_window.py

from PyQt5.QtWidgets import (
    QDialog, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QHBoxLayout, QMessageBox, QTextEdit, QTabWidget, QScrollArea,
    QFrame
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QFile, QIODevice, QTimer, Qt
from core.tunnel_config import load_server_list, save_server_list
from core.ssh_manager import SSHManager
from gui.add_server_dialog import AddServerDialog
from gui.ssh_terminal_dialog import SSHTerminalDialog
from gui.icon_data import get_icon
from gui.ssh_terminal_widget import SSHTerminalWidget
from gui.theme import Theme
from gui.components import HeaderBar, ServerCard, ServerFormCard
from gui.components.bottom_panel import ConnectionStatus
from gui.styled_message_box import StyledMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(get_icon())

        self.ssh_managers = {}  # 서버별 SSH 매니저 저장 {index: SSHManager}
        self.connected_indices = set()  # 연결된 서버 인덱스 집합
        self.server_cards = []  # 서버 카드 위젯 리스트
        self.server_form_card = None  # 서버 추가/수정 폼 카드
        self.editing_server_index = None  # 수정 중인 서버 인덱스

        self.setWindowTitle("Hshell")
        self.setGeometry(100, 100, 1200, 800)
        
        # 전역 스타일시트 적용
        self.setStyleSheet(Theme.get_global_stylesheet())

        self.central_widget = QWidget()
        self.central_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.BACKGROUND};
            }}
        """)
        self.setCentralWidget(self.central_widget)

        # 메인 레이아웃 (피그마 App.tsx 구조)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.central_widget.setLayout(main_layout)

        # 상단 타이틀바 (slate-800)
        self.header_bar = HeaderBar()
        self.header_bar.settings_clicked.connect(self.show_settings)
        main_layout.addWidget(self.header_bar)

        # 메인 콘텐츠 영역 (단일 열 레이아웃)
        content_widget = QWidget()
        content_widget.setObjectName("contentWidget")
        content_widget.setStyleSheet(f"""
            QWidget#contentWidget {{
                background-color: {Theme.BACKGROUND};
            }}
        """)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)
        content_widget.setLayout(content_layout)

        # 메인 카드 (TunnelManager를 포함하는 큰 흰색 카드)
        main_card = QFrame()
        main_card.setObjectName("mainCard")
        main_card.setStyleSheet(f"""
            QFrame#mainCard {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
            }}
        """)
        main_card_layout = QVBoxLayout()
        main_card_layout.setContentsMargins(0, 0, 0, 0)
        main_card_layout.setSpacing(0)

        # 카드 헤더 (slate-50 배경)
        card_header = QWidget()
        card_header.setObjectName("cardHeader")
        card_header.setStyleSheet(f"""
            QWidget#cardHeader {{
                background-color: #f8fafc;
                border-bottom: 1px solid {Theme.BORDER_SOLID};
                border-top-left-radius: {Theme.RADIUS_LG};
                border-top-right-radius: {Theme.RADIUS_LG};
            }}
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(12)
        
        hero_layout = QVBoxLayout()
        hero_layout.setSpacing(6)
        
        self.dashboard_badge = QLabel("HSHELL · CONTROL CENTER")
        self.dashboard_badge.setStyleSheet(f"""
            QLabel {{
                text-transform: uppercase;
                letter-spacing: 1px;
                font-size: 11px;
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                color: {Theme.MUTED_FOREGROUND};
                background-color: rgba(15, 23, 42, 0.05);
                border-radius: {Theme.RADIUS_SM};
                padding: 4px 10px;
            }}
        """)
        hero_layout.addWidget(self.dashboard_badge, alignment=Qt.AlignLeft)
        
        self.dashboard_title = QLabel("Hshell")
        self.dashboard_title.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_2XL};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
            background-color: transparent;
        """)
        hero_layout.addWidget(self.dashboard_title, alignment=Qt.AlignLeft)
        
        self.dashboard_subtitle = QLabel("SSH 터널·스크립트를 한 화면에서 관리하는 운영 대시보드")
        self.dashboard_subtitle.setStyleSheet(f"""
            color: {Theme.MUTED_FOREGROUND};
            font-size: {Theme.FONT_SIZE_BASE};
            background-color: transparent;
        """)
        hero_layout.addWidget(self.dashboard_subtitle, alignment=Qt.AlignLeft)
        
        header_layout.addLayout(hero_layout, stretch=1)
        
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(8)
        stats_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.dashboard_stats = QLabel()
        self.dashboard_stats.setFixedHeight(40)
        self.dashboard_stats.setStyleSheet(f"""
            QLabel {{
                padding: 8px 16px;
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                background-color: {Theme.CARD};
                color: {Theme.FOREGROUND};
                font-size: {Theme.FONT_SIZE_SM};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            }}
        """)
        stats_layout.addWidget(self.dashboard_stats, alignment=Qt.AlignRight)
        
        self.dashboard_timestamp = QLabel()
        self.dashboard_timestamp.setStyleSheet(f"""
            color: {Theme.MUTED_FOREGROUND};
            font-size: {Theme.FONT_SIZE_SM};
        """)
        stats_layout.addWidget(self.dashboard_timestamp, alignment=Qt.AlignRight)
        
        header_layout.addLayout(stats_layout)
        card_header.setLayout(header_layout)
        main_card_layout.addWidget(card_header)

        # 카드 본문 (TunnelManager)
        card_body = QWidget()
        card_body.setObjectName("cardBody")
        card_body.setStyleSheet(f"""
            QWidget#cardBody {{
                background-color: {Theme.CARD};
            }}
        """)
        card_body_layout = QVBoxLayout()
        card_body_layout.setContentsMargins(24, 24, 24, 24)
        card_body_layout.setSpacing(16)

        # 서버 목록 영역
        server_panel = QVBoxLayout()
        server_panel.setSpacing(16)

        # 서버 목록 헤더
        server_header = QHBoxLayout()
        server_header.setSpacing(16)
        
        title_label = QLabel("연결 서버 목록")
        title_label.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_XL};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
            background-color: transparent;
        """)
        server_header.addWidget(title_label)
        server_header.addStretch()

        # 서버 추가 버튼
        self.add_button = QPushButton("+ 새 서버 추가")
        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_FOREGROUND};
                border: 2px solid {Theme.PRIMARY};
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} {Theme.SPACING_LG};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                font-size: {Theme.FONT_SIZE_SM};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: #1a1a2e;
                border: 2px solid #1a1a2e;
            }}
        """)
        self.add_button.clicked.connect(self.add_server)
        server_header.addWidget(self.add_button)

        server_panel.addLayout(server_header)

        # 서버 카드 컨테이너
        self.server_container = QWidget()
        self.server_container.setObjectName("serverContainer")
        self.server_container.setStyleSheet(f"""
            QWidget#serverContainer {{
                background-color: {Theme.CARD};
            }}
        """)
        self.server_layout = QVBoxLayout()
        self.server_layout.setSpacing(16)
        self.server_layout.setContentsMargins(0, 0, 0, 0)
        self.server_container.setLayout(self.server_layout)
        
        server_panel.addWidget(self.server_container)
        
        card_body_layout.addLayout(server_panel)
        card_body.setLayout(card_body_layout)
        
        # 스크롤 영역으로 카드 본문 감싸기
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {Theme.CARD};
                border: none;
            }}
            QScrollArea > QWidget {{
                background-color: {Theme.CARD};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {Theme.MUTED};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.MUTED_FOREGROUND};
                border-radius: 5px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.PRIMARY};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        scroll_area.setWidget(card_body)
        main_card_layout.addWidget(scroll_area)
        
        main_card.setLayout(main_card_layout)
        content_layout.addWidget(main_card, stretch=1)

        # 하단 컨트롤 패널 (ConnectionStatus + 토글 버튼)
        bottom_controls = QHBoxLayout()
        bottom_controls.setSpacing(12)
        
        # ConnectionStatus (피그마 디자인)
        self.connection_status = ConnectionStatus()
        bottom_controls.addWidget(self.connection_status)
        
        bottom_controls.addStretch()
        
        # 스크립트 실행 버튼
        self.script_btn = QPushButton("📄 스크립트 실행")
        self.script_btn.setProperty("showScript", False)
        self.script_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.CARD};
                color: {Theme.FOREGROUND};
                border: 2px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} {Theme.SPACING_LG};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                font-size: {Theme.FONT_SIZE_SM};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT};
                border: 2px solid {Theme.PRIMARY};
            }}
            QPushButton[showScript="true"] {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_FOREGROUND};
                border: 2px solid {Theme.PRIMARY};
            }}
        """)
        self.script_btn.clicked.connect(self.toggle_script_panel)
        bottom_controls.addWidget(self.script_btn)
        
        # 터미널 버튼
        self.terminal_btn = QPushButton("💻 터미널")
        self.terminal_btn.setProperty("showTerminal", False)
        self.terminal_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.CARD};
                color: {Theme.FOREGROUND};
                border: 2px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} {Theme.SPACING_LG};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                font-size: {Theme.FONT_SIZE_SM};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT};
                border: 2px solid {Theme.PRIMARY};
            }}
            QPushButton[showTerminal="true"] {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_FOREGROUND};
                border: 2px solid {Theme.PRIMARY};
            }}
        """)
        self.terminal_btn.clicked.connect(self.toggle_terminal_panel)
        bottom_controls.addWidget(self.terminal_btn)
        
        content_layout.addLayout(bottom_controls)
        
        # 스크립트 패널 (토글 가능, 피그마 디자인)
        self.script_panel = QFrame()
        self.script_panel.setVisible(False)
        self.script_panel.setObjectName("scriptPanel")
        self.script_panel.setStyleSheet(f"""
            QFrame#scriptPanel {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
            }}
        """)
        script_layout = QVBoxLayout()
        script_layout.setContentsMargins(0, 0, 0, 0)
        script_layout.setSpacing(0)
        
        # 스크립트 헤더 (slate-800)
        script_header = QWidget()
        script_header.setObjectName("scriptHeader")
        script_header.setStyleSheet(f"""
            QWidget#scriptHeader {{
                background-color: #1e293b;
                border-top-left-radius: {Theme.RADIUS_LG};
                border-top-right-radius: {Theme.RADIUS_LG};
            }}
            QWidget#scriptHeader QLabel {{
                background-color: transparent;
            }}
        """)
        script_header_layout = QHBoxLayout()
        script_header_layout.setContentsMargins(16, 12, 16, 12)
        script_header_layout.setSpacing(8)
        
        script_icon = QLabel("📄")
        script_icon.setStyleSheet("font-size: 16px;")
        script_header_layout.addWidget(script_icon)
        
        script_title = QLabel("스크립트 실행")
        script_title.setStyleSheet(f"""
            color: white;
            font-size: {Theme.FONT_SIZE_BASE};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            background-color: transparent;
        """)
        script_header_layout.addWidget(script_title)
        script_header_layout.addStretch()
        
        close_script_btn = QPushButton("✕")
        close_script_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                border-radius: {Theme.RADIUS_SM};
                padding: 4px 8px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: #334155;
            }}
        """)
        close_script_btn.clicked.connect(self.toggle_script_panel)
        script_header_layout.addWidget(close_script_btn)
        
        script_header.setLayout(script_header_layout)
        script_layout.addWidget(script_header)
        
        # 스크립트 본문
        script_body = QTextEdit()
        script_body.setPlaceholderText("실행할 스크립트를 입력하세요...")
        script_body.setMinimumHeight(300)
        script_body.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.CARD};
                border: none;
                border-bottom-left-radius: {Theme.RADIUS_LG};
                border-bottom-right-radius: {Theme.RADIUS_LG};
                padding: 16px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: {Theme.FONT_SIZE_SM};
            }}
        """)
        script_layout.addWidget(script_body)
        
        self.script_panel.setLayout(script_layout)
        content_layout.addWidget(self.script_panel)
        
        # 터미널 패널 (토글 가능, 피그마 디자인)
        self.terminal_panel = QFrame()
        self.terminal_panel.setVisible(False)
        self.terminal_panel.setObjectName("terminalPanel")
        self.terminal_panel.setStyleSheet(f"""
            QFrame#terminalPanel {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
            }}
        """)
        terminal_layout = QVBoxLayout()
        terminal_layout.setContentsMargins(0, 0, 0, 0)
        terminal_layout.setSpacing(0)
        
        # 터미널 헤더 (slate-800)
        terminal_header = QWidget()
        terminal_header.setObjectName("terminalHeader")
        terminal_header.setStyleSheet(f"""
            QWidget#terminalHeader {{
                background-color: #1e293b;
                border-top-left-radius: {Theme.RADIUS_LG};
                border-top-right-radius: {Theme.RADIUS_LG};
            }}
            QWidget#terminalHeader QLabel {{
                background-color: transparent;
            }}
        """)
        terminal_header_layout = QHBoxLayout()
        terminal_header_layout.setContentsMargins(16, 12, 16, 12)
        terminal_header_layout.setSpacing(8)
        
        terminal_icon = QLabel("💻")
        terminal_icon.setStyleSheet("font-size: 16px;")
        terminal_header_layout.addWidget(terminal_icon)
        
        terminal_title = QLabel("터미널")
        terminal_title.setStyleSheet(f"""
            color: white;
            font-size: {Theme.FONT_SIZE_BASE};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            background-color: transparent;
        """)
        terminal_header_layout.addWidget(terminal_title)
        terminal_header_layout.addStretch()
        
        close_terminal_btn = QPushButton("✕")
        close_terminal_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: white;
                border: none;
                border-radius: {Theme.RADIUS_SM};
                padding: 4px 8px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: #334155;
            }}
        """)
        close_terminal_btn.clicked.connect(self.toggle_terminal_panel)
        terminal_header_layout.addWidget(close_terminal_btn)
        
        terminal_header.setLayout(terminal_header_layout)
        terminal_layout.addWidget(terminal_header)
        
        # 터미널 본문 (검정 배경, 녹색 텍스트)
        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setMinimumHeight(250)
        self.terminal_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: #000000;
                color: #10b981;
                border: none;
                border-bottom-left-radius: {Theme.RADIUS_LG};
                border-bottom-right-radius: {Theme.RADIUS_LG};
                padding: 16px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: {Theme.FONT_SIZE_SM};
            }}
        """)
        self.terminal_output.setText("Microsoft Windows [Version 10.0.19045.3693]\n(c) Microsoft Corporation. All rights reserved.\n\nC:\\Users\\Admin> _")
        terminal_layout.addWidget(self.terminal_output)
        
        self.terminal_panel.setLayout(terminal_layout)
        content_layout.addWidget(self.terminal_panel)
        
        main_layout.addWidget(content_widget, stretch=1)

        # 서버 목록 불러오기
        self.servers = load_server_list()
        self.refresh_server_list()

        # 연결 상태 확인 타이머 추가
        self.connection_check_timer = QTimer(self)
        self.connection_check_timer.timeout.connect(self.check_all_connections)
        self.connection_check_timer.start(5000)  # 5초마다 확인
    
    def toggle_script_panel(self):
        """스크립트 패널 토글"""
        is_visible = self.script_panel.isVisible()
        self.script_panel.setVisible(not is_visible)
        self.script_btn.setProperty("showScript", not is_visible)
        self.script_btn.style().unpolish(self.script_btn)
        self.script_btn.style().polish(self.script_btn)
        
        # 터미널이 열려있으면 닫기
        if not is_visible and self.terminal_panel.isVisible():
            self.terminal_panel.setVisible(False)
            self.terminal_btn.setProperty("showTerminal", False)
            self.terminal_btn.style().unpolish(self.terminal_btn)
            self.terminal_btn.style().polish(self.terminal_btn)
    
    def toggle_terminal_panel(self):
        """터미널 패널 토글"""
        is_visible = self.terminal_panel.isVisible()
        self.terminal_panel.setVisible(not is_visible)
        self.terminal_btn.setProperty("showTerminal", not is_visible)
        self.terminal_btn.style().unpolish(self.terminal_btn)
        self.terminal_btn.style().polish(self.terminal_btn)
        
        # 스크립트가 열려있으면 닫기
        if not is_visible and self.script_panel.isVisible():
            self.script_panel.setVisible(False)
            self.script_btn.setProperty("showScript", False)
            self.script_btn.style().unpolish(self.script_btn)
            self.script_btn.style().polish(self.script_btn)

    def refresh_server_list(self):
        """서버 목록을 카드 형태로 갱신"""
        # 기존 카드 제거
        for card in self.server_cards:
            card.deleteLater()
        self.server_cards.clear()

        # 폼 카드가 있으면 먼저 추가
        if self.server_form_card:
            self.server_layout.addWidget(self.server_form_card)

        # 새로운 카드 생성
        for i, server in enumerate(self.servers):
            is_connected = i in self.connected_indices
            card = ServerCard(i, server, is_connected)
            
            # 시그널 연결
            card.edit_clicked.connect(self.edit_server)
            card.delete_clicked.connect(self.delete_server)
            card.connect_clicked.connect(self.connect_server)
            card.disconnect_clicked.connect(self.disconnect_server)
            card.ssh_clicked.connect(self.open_ssh_console)
            
            self.server_layout.addWidget(card)
            self.server_cards.append(card)

        # 스페이서 추가 (아래쪽 여백)
        self.server_layout.addStretch()
        
        # 연결 상태 업데이트
        self.connection_status.update_status(len(self.connected_indices))
        self.update_dashboard_header()

    def add_server(self):
        """서버 추가 폼 표시"""
        if self.server_form_card:
            # 이미 폼이 열려있으면 닫기
            self.close_server_form()
            return
        
        self.editing_server_index = None
        self.server_form_card = ServerFormCard()
        self.server_form_card.save_clicked.connect(self.on_server_form_save)
        self.server_form_card.cancel_clicked.connect(self.close_server_form)
        
        # 기존 카드들을 모두 제거하고 폼을 맨 위에 추가
        for card in self.server_cards:
            self.server_layout.removeWidget(card)
        
        self.server_layout.insertWidget(0, self.server_form_card)
        
        # 카드들을 다시 추가
        for card in self.server_cards:
            self.server_layout.addWidget(card)

    def connect_server(self, index):
        if index < 0 or index >= len(self.servers):
            self.terminal_output.append("\n[오류] 잘못된 서버 인덱스입니다.")
            return

        if index in self.connected_indices:
            self.terminal_output.append(f"\n[경고] {self.servers[index]['name']} 서버는 이미 연결되어 있습니다.")
            return

        server_info = self.servers[index]
        ssh_manager = SSHManager(server_info)

        self.terminal_output.append(f"\n[연결 시도] {server_info['name']} 서버 연결 시도 중...")
        success = ssh_manager.connect()
        
        if success:
            self.ssh_managers[index] = ssh_manager
            self.connected_indices.add(index)
            self.refresh_server_list()
            self.terminal_output.append(f"\n[연결 성공] {server_info['name']} 서버에 연결되었습니다.")
        else:
            self.terminal_output.append(f"\n[연결 실패] {server_info['name']} 서버 연결에 실패했습니다.")

    def disconnect_server(self, index):
        if index < 0 or index >= len(self.servers):
            self.terminal_output.append("\n[오류] 잘못된 서버 인덱스입니다.")
            return

        if index not in self.connected_indices:
            self.terminal_output.append(f"\n[경고] {self.servers[index]['name']} 서버는 연결되어 있지 않습니다.")
            return

        if index in self.ssh_managers:
            self.ssh_managers[index].disconnect()
            del self.ssh_managers[index]
            self.connected_indices.remove(index)
            self.refresh_server_list()
            self.terminal_output.append(f"\n[연결 종료] {self.servers[index]['name']} 서버 연결이 종료되었습니다.")

    def edit_server(self, index):
        """서버 수정 폼 표시"""
        if index < 0 or index >= len(self.servers):
            self.terminal_output.append("\n[오류] 잘못된 서버 인덱스입니다.")
            return
        
        if self.server_form_card:
            # 이미 폼이 열려있으면 닫기
            self.close_server_form()
        
        current_data = self.servers[index]
        self.editing_server_index = index
        self.server_form_card = ServerFormCard(server_data=current_data)
        self.server_form_card.save_clicked.connect(self.on_server_form_save)
        self.server_form_card.cancel_clicked.connect(self.close_server_form)
        
        # 기존 카드들을 모두 제거하고 폼을 맨 위에 추가
        for card in self.server_cards:
            self.server_layout.removeWidget(card)
        
        self.server_layout.insertWidget(0, self.server_form_card)
        
        # 카드들을 다시 추가
        for card in self.server_cards:
            self.server_layout.addWidget(card)
    
    def on_server_form_save(self, server_data):
        """서버 폼 저장"""
        if self.editing_server_index is not None:
            # 수정
            self.servers[self.editing_server_index] = server_data
            self.terminal_output.append(f"\n[성공] {server_data['name']} 서버 정보가 수정되었습니다.")
        else:
            # 추가
            self.servers.append(server_data)
            self.terminal_output.append(f"\n[성공] {server_data['name']} 서버가 추가되었습니다.")
        
        save_server_list(self.servers)
        self.close_server_form()
        self.refresh_server_list()
    
    def close_server_form(self):
        """서버 폼 닫기"""
        if self.server_form_card:
            self.server_layout.removeWidget(self.server_form_card)
            self.server_form_card.deleteLater()
            self.server_form_card = None
            self.editing_server_index = None

    def delete_server(self, index):
        if index < 0 or index >= len(self.servers):
            self.terminal_output.append("\n[오류] 잘못된 서버 인덱스입니다.")
            return

        name = self.servers[index]['name']
        confirm = StyledMessageBox.question(self, "삭제 확인", f"{name} 서버를 삭제할까요?",
                                    QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            # 연결된 상태라면 먼저 연결 해제
            if index in self.connected_indices:
                self.ssh_managers[index].disconnect()
                del self.ssh_managers[index]
                self.connected_indices.remove(index)
            
            del self.servers[index]
            save_server_list(self.servers)
            self.refresh_server_list()
            self.terminal_output.append(f"\n[삭제] {name} 서버가 삭제되었습니다.")

    def open_ssh_console(self, index):
        """SSH 콘솔을 터미널 패널에서 엽니다"""
        if index < 0 or index >= len(self.servers):
            self.terminal_output.append("\n[오류] 잘못된 서버 인덱스입니다.")
            return

        if index not in self.connected_indices or index not in self.ssh_managers:
            self.terminal_output.append("\n[경고] 먼저 서버에 연결하세요.")
            return

        server_name = self.servers[index]['name']
        self.terminal_output.append(f"\n[SSH] {server_name} 서버 SSH 콘솔 시작...")
        
        # 터미널 패널 열기
        if not self.terminal_panel.isVisible():
            self.toggle_terminal_panel()

    def check_all_connections(self):
        """
        모든 연결의 상태를 주기적으로 확인하고 업데이트
        """
        disconnected_indices = set()
        
        # 각 연결의 상태 확인
        for index in list(self.connected_indices):
            if index in self.ssh_managers:
                ssh_manager = self.ssh_managers[index]
                if not ssh_manager.is_connected():
                    disconnected_indices.add(index)
                    self.terminal_output.append(f"\n[경고] {self.servers[index]['name']} 서버 연결이 끊어졌습니다.")
        
        # 끊어진 연결 정리
        for index in disconnected_indices:
            if index in self.ssh_managers:
                self.ssh_managers[index].disconnect()
                del self.ssh_managers[index]
            if index in self.connected_indices:
                self.connected_indices.remove(index)
        
        # UI 업데이트
        if disconnected_indices:
            self.refresh_server_list()
    
    def show_settings(self):
        """설정 다이얼로그 표시 (추후 구현)"""
        self.terminal_output.append("\n[정보] 설정 기능은 추후 구현 예정입니다.")

    def update_dashboard_header(self):
        """상단 카드 헤더의 통계 텍스트를 갱신"""
        total_servers = len(self.servers)
        connected_servers = len(self.connected_indices)
        self.dashboard_stats.setText(
            f"연결 {connected_servers} / 총 {total_servers} 서버"
        )
        from datetime import datetime
        self.dashboard_timestamp.setText(
            f"업데이트 {datetime.now().strftime('%H:%M:%S')}"
        )
