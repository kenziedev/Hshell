# gui/components/server_card.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from gui.theme import Theme


class ServerCard(QWidget):
    """
    서버 카드 컴포넌트
    Figma 디자인: 화이트 카드 배경에 서버 정보 + 액션 버튼들
    """
    edit_clicked = pyqtSignal(int)
    delete_clicked = pyqtSignal(int)
    connect_clicked = pyqtSignal(int)
    disconnect_clicked = pyqtSignal(int)
    ssh_clicked = pyqtSignal(int)
    
    def __init__(self, server_index, server_data, is_connected=False, parent=None):
        super().__init__(parent)
        self.server_index = server_index
        self.server_data = server_data
        self.is_connected = is_connected
        self.init_ui()
    
    def init_ui(self):
        # 피그마 TunnelManager의 서버 카드 스타일 적용
        self.setObjectName("serverCard")
        self.setStyleSheet(f"""
            QWidget#serverCard {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
            }}
            QWidget#serverCard:hover {{
                border: 1px solid {Theme.PRIMARY};
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)  # 피그마 CardContent 패딩: 24px
        layout.setSpacing(16)
        
        # 상단: 서버명 + 연결 상태 (피그마 TunnelManager 스타일)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        server_name = QLabel(self.server_data['name'])
        server_name.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_LG};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
            background-color: transparent;
            padding: 0px;
        """)
        header_layout.addWidget(server_name)
        
        if self.is_connected:
            status_badge = QLabel("연결됨")
            status_badge.setStyleSheet(f"""
                background-color: {Theme.STATUS_ACTIVE_BG};
                color: {Theme.STATUS_ACTIVE_TEXT};
                border: none;
                border-radius: {Theme.RADIUS_SM};
                padding: 4px 12px;
                font-size: {Theme.FONT_SIZE_SM};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            """)
            header_layout.addWidget(status_badge)
        else:
            status_badge = QLabel("연결 안됨")
            status_badge.setStyleSheet(f"""
                background-color: {Theme.STATUS_INACTIVE_BG};
                color: {Theme.STATUS_INACTIVE_TEXT};
                border: none;
                border-radius: {Theme.RADIUS_SM};
                padding: 4px 12px;
                font-size: {Theme.FONT_SIZE_SM};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            """)
            header_layout.addWidget(status_badge)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # 중간: 서버 정보 (피그마 스타일)
        info_label = QLabel(f"{self.server_data['username']}@{self.server_data['host']}:{self.server_data['port']}")
        info_label.setStyleSheet(f"""
            color: {Theme.MUTED_FOREGROUND};
            font-size: {Theme.FONT_SIZE_SM};
            background-color: transparent;
            padding: 0px;
        """)
        layout.addWidget(info_label)
        
        # 터널 정보 (피그마 Badge 스타일)
        if self.server_data.get('tunnels'):
            tunnel_count = len(self.server_data['tunnels'])
            tunnel_label = QLabel(f"{tunnel_count}개 터널")
            tunnel_label.setStyleSheet(f"""
                color: {Theme.FOREGROUND};
                background-color: transparent;
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_SM};
                padding: 4px 8px;
                font-size: {Theme.FONT_SIZE_SM};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            """)
            tunnel_label.setMaximumWidth(100)
            layout.addWidget(tunnel_label)
        
        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"""
            background-color: {Theme.BORDER_SOLID};
            max-height: 1px;
        """)
        layout.addWidget(separator)
        
        # 하단: 액션 버튼들 (피그마 TunnelManager Table Actions 스타일)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # 연결/해제 버튼 (Play/Square 아이콘)
        if self.is_connected:
            disconnect_btn = QPushButton("⏹ 중지")
            disconnect_btn.setProperty("buttonStyle", "outline")
            disconnect_btn.clicked.connect(lambda: self.disconnect_clicked.emit(self.server_index))
            button_layout.addWidget(disconnect_btn)
            
            # SSH 버튼
            ssh_btn = QPushButton("SSH")
            ssh_btn.clicked.connect(lambda: self.ssh_clicked.emit(self.server_index))
            button_layout.addWidget(ssh_btn)
        else:
            connect_btn = QPushButton("▶ 시작")
            connect_btn.clicked.connect(lambda: self.connect_clicked.emit(self.server_index))
            button_layout.addWidget(connect_btn)
        
        button_layout.addStretch()
        
        # 수정 버튼
        edit_btn = QPushButton("✏ 수정")
        edit_btn.setProperty("buttonStyle", "outline")
        edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.server_index))
        button_layout.addWidget(edit_btn)
        
        # 삭제 버튼
        delete_btn = QPushButton("🗑 삭제")
        delete_btn.setProperty("buttonStyle", "destructive")
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.server_index))
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def update_connection_status(self, is_connected):
        """연결 상태 업데이트"""
        self.is_connected = is_connected
        # UI 재구성
        # 기존 레이아웃 제거
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # UI 재생성
        self.init_ui()

