# gui/components/bottom_panel.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QFrame, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from gui.theme import Theme


class ConnectionStatus(QWidget):
    """
    연결 상태 표시 컴포넌트 (피그마 ConnectionStatus.tsx 스타일)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.connected_count = 0
        self.init_ui()
    
    def init_ui(self):
        # 피그마 스타일: 카드 배경에 상태 정보들
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: 12px 16px;
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(24)
        
        # 네트워크 상태
        network_layout = QHBoxLayout()
        network_layout.setSpacing(8)
        network_icon = QLabel("📶")
        network_icon.setStyleSheet("font-size: 16px;")
        network_layout.addWidget(network_icon)
        self.network_label = QLabel("네트워크: 연결됨")
        self.network_label.setStyleSheet(f"""
            color: #059669;
            font-size: {Theme.FONT_SIZE_SM};
            font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            background-color: transparent;
        """)
        network_layout.addWidget(self.network_label)
        layout.addLayout(network_layout)
        
        # 활성 터널 수
        tunnel_layout = QHBoxLayout()
        tunnel_layout.setSpacing(8)
        tunnel_icon = QLabel("📊")
        tunnel_icon.setStyleSheet("font-size: 16px;")
        tunnel_layout.addWidget(tunnel_icon)
        self.tunnel_label = QLabel("활성 터널: 0개")
        self.tunnel_label.setStyleSheet(f"""
            color: {Theme.FOREGROUND};
            font-size: {Theme.FONT_SIZE_SM};
            font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            background-color: transparent;
        """)
        tunnel_layout.addWidget(self.tunnel_label)
        layout.addLayout(tunnel_layout)
        
        # 실행 중 뱃지
        self.status_badge = QLabel("● 실행 중")
        self.status_badge.setStyleSheet(f"""
            background-color: {Theme.PRIMARY};
            color: {Theme.PRIMARY_FOREGROUND};
            border-radius: {Theme.RADIUS_SM};
            padding: 4px 12px;
            font-size: {Theme.FONT_SIZE_SM};
            font-weight: {Theme.FONT_WEIGHT_MEDIUM};
        """)
        layout.addWidget(self.status_badge)
        
        layout.addStretch()
        
        # 마지막 업데이트 시간
        from datetime import datetime
        self.time_label = QLabel(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")
        self.time_label.setStyleSheet(f"""
            color: {Theme.MUTED_FOREGROUND};
            font-size: {Theme.FONT_SIZE_SM};
            background-color: transparent;
        """)
        layout.addWidget(self.time_label)
        
        self.setLayout(layout)
    
    def update_status(self, connected_count):
        """연결 상태 업데이트"""
        from datetime import datetime
        self.connected_count = connected_count
        self.tunnel_label.setText(f"활성 터널: {connected_count}개")
        self.time_label.setText(f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')}")
        
        if connected_count == 0:
            self.tunnel_label.setStyleSheet(f"""
                color: {Theme.MUTED_FOREGROUND};
                font-size: {Theme.FONT_SIZE_SM};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                background-color: transparent;
            """)
        else:
            self.tunnel_label.setStyleSheet(f"""
                color: #2563eb;
                font-size: {Theme.FONT_SIZE_SM};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                background-color: transparent;
            """)


class BottomPanel(QWidget):
    """
    하단 패널 컴포넌트 - ConnectionStatus + 토글 가능한 스크립트/터미널
    """
    script_toggled = pyqtSignal(bool)
    terminal_toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.script_visible = False
        self.terminal_visible = False
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(8)
        
        # 컨트롤 바
        control_bar = QHBoxLayout()
        control_bar.setSpacing(12)
        
        # 연결 상태
        self.connection_status = ConnectionStatus()
        control_bar.addWidget(self.connection_status)
        
        control_bar.addStretch()
        
        # 스크립트 실행 버튼
        self.script_btn = QPushButton("📝 스크립트 실행")
        self.script_btn.setProperty("buttonStyle", "outline")
        self.script_btn.setCheckable(True)
        self.script_btn.clicked.connect(self.toggle_script)
        control_bar.addWidget(self.script_btn)
        
        # 터미널 버튼
        self.terminal_btn = QPushButton("💻 터미널")
        self.terminal_btn.setProperty("buttonStyle", "outline")
        self.terminal_btn.setCheckable(True)
        self.terminal_btn.clicked.connect(self.toggle_terminal)
        control_bar.addWidget(self.terminal_btn)
        
        main_layout.addLayout(control_bar)
        
        # 스크립트 패널 (숨김 가능)
        self.script_panel = self.create_script_panel()
        self.script_panel.setVisible(False)
        main_layout.addWidget(self.script_panel)
        
        # 터미널 패널 (숨김 가능)
        self.terminal_panel = self.create_terminal_panel()
        self.terminal_panel.setVisible(False)
        main_layout.addWidget(self.terminal_panel)
        
        self.setLayout(main_layout)
    
    def create_script_panel(self):
        """스크립트 실행 패널 생성"""
        panel = QFrame()
        panel.setProperty("frameStyle", "card")
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 헤더
        header = QHBoxLayout()
        title = QLabel("📝 스크립트 실행")
        title.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_LG};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
        """)
        header.addWidget(title)
        header.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setProperty("buttonStyle", "ghost")
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(lambda: self.toggle_script())
        header.addWidget(close_btn)
        
        layout.addLayout(header)
        
        # 스크립트 입력 영역
        script_edit = QTextEdit()
        script_edit.setPlaceholderText("실행할 스크립트를 입력하세요...")
        script_edit.setMinimumHeight(200)
        layout.addWidget(script_edit)
        
        # 실행 버튼
        exec_btn = QPushButton("실행")
        exec_btn.setFixedWidth(100)
        layout.addWidget(exec_btn, alignment=Qt.AlignRight)
        
        panel.setLayout(layout)
        return panel
    
    def create_terminal_panel(self):
        """터미널 패널 생성"""
        panel = QFrame()
        panel.setProperty("frameStyle", "card")
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 헤더
        header = QHBoxLayout()
        title = QLabel("💻 터미널")
        title.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_LG};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
        """)
        header.addWidget(title)
        header.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setProperty("buttonStyle", "ghost")
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(lambda: self.toggle_terminal())
        header.addWidget(close_btn)
        
        layout.addLayout(header)
        
        # 터미널 영역
        terminal_output = QTextEdit()
        terminal_output.setReadOnly(True)
        terminal_output.setMinimumHeight(200)
        terminal_output.setStyleSheet(f"""
            QTextEdit {{
                background-color: #1a1a1a;
                color: #10b981;
                border: none;
                border-radius: {Theme.RADIUS_SM};
                padding: {Theme.SPACING_MD};
                font-family: Consolas, Monaco, monospace;
                font-size: {Theme.FONT_SIZE_SM};
            }}
        """)
        terminal_output.setText("Microsoft Windows [Version 10.0.19045.3693]\n(c) Microsoft Corporation. All rights reserved.\n\nC:\\Users\\Admin> _")
        layout.addWidget(terminal_output)
        
        panel.setLayout(layout)
        return panel
    
    def toggle_script(self):
        """스크립트 패널 토글"""
        self.script_visible = not self.script_visible
        self.script_panel.setVisible(self.script_visible)
        self.script_btn.setChecked(self.script_visible)
        
        # 터미널이 열려있으면 닫기
        if self.script_visible and self.terminal_visible:
            self.terminal_visible = False
            self.terminal_panel.setVisible(False)
            self.terminal_btn.setChecked(False)
        
        self.script_toggled.emit(self.script_visible)
    
    def toggle_terminal(self):
        """터미널 패널 토글"""
        self.terminal_visible = not self.terminal_visible
        self.terminal_panel.setVisible(self.terminal_visible)
        self.terminal_btn.setChecked(self.terminal_visible)
        
        # 스크립트가 열려있으면 닫기
        if self.terminal_visible and self.script_visible:
            self.script_visible = False
            self.script_panel.setVisible(False)
            self.script_btn.setChecked(False)
        
        self.terminal_toggled.emit(self.terminal_visible)
    
    def update_connection_status(self, count):
        """연결 상태 업데이트"""
        self.connection_status.update_status(count)

