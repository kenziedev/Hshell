# gui/server_form_dialog.py
"""
서버 추가/수정 다이얼로그
피그마 ServerFormCard 스타일을 다이얼로그로 구현
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGridLayout, QFrame, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from gui.theme import Theme


class TunnelRow(QWidget):
    """터널 입력 행"""
    remove_clicked = pyqtSignal()
    
    def __init__(self, tunnel_data=None, parent=None):
        super().__init__(parent)
        self.tunnel_data = tunnel_data or {}
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #f8fafc;
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: 12px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # 터널명
        self.tunnel_name = QLineEdit(self.tunnel_data.get('name', ''))
        self.tunnel_name.setPlaceholderText("Database")
        layout.addWidget(self.tunnel_name, stretch=2)
        
        # 로컬 포트
        self.local_port = QLineEdit(str(self.tunnel_data.get('local', '')))
        self.local_port.setPlaceholderText("3306")
        layout.addWidget(self.local_port, stretch=1)
        
        # 원격 호스트
        self.remote_host = QLineEdit(self.tunnel_data.get('remote_host', ''))
        self.remote_host.setPlaceholderText("localhost")
        layout.addWidget(self.remote_host, stretch=2)
        
        # 원격 포트
        self.remote_port = QLineEdit(str(self.tunnel_data.get('remote_port', '')))
        self.remote_port.setPlaceholderText("3306")
        layout.addWidget(self.remote_port, stretch=1)
        
        # 삭제 버튼
        delete_btn = QPushButton("✕")
        delete_btn.setProperty("buttonStyle", "ghost")
        delete_btn.setFixedSize(32, 32)
        delete_btn.clicked.connect(self.remove_clicked.emit)
        layout.addWidget(delete_btn)
    
    def get_data(self):
        """터널 데이터 반환"""
        return {
            'name': self.tunnel_name.text().strip(),
            'local': int(self.local_port.text()) if self.local_port.text().strip() else 0,
            'remote_host': self.remote_host.text().strip(),
            'remote_port': int(self.remote_port.text()) if self.remote_port.text().strip() else 0
        }


class ServerFormDialog(QDialog):
    """서버 추가/수정 다이얼로그"""
    
    def __init__(self, server_data=None, parent=None):
        super().__init__(parent)
        self.server_data = server_data
        self.tunnel_rows = []
        self.result_data = None
        
        self.setWindowTitle("서버 수정" if server_data else "새 서버 추가")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # 헤더
        header_layout = QHBoxLayout()
        title = QLabel("✏️ 서버 설정 수정" if self.server_data else "➕ 새 서버 추가")
        title.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_XL};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(24)
        
        # 서버 정보 섹션
        self.create_server_section(scroll_layout)
        
        # 터널링 정보 섹션
        self.create_tunnel_section(scroll_layout)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, stretch=1)
        
        # 하단 버튼
        self.create_footer_buttons(main_layout)
        
        # 스타일 적용
        self.setStyleSheet(self.get_dialog_stylesheet())
    
    def create_server_section(self, layout):
        """서버 정보 섹션"""
        section_title = QLabel("서버 정보")
        section_title.setObjectName("sectionTitle")
        layout.addWidget(section_title)
        
        grid = QGridLayout()
        grid.setSpacing(12)
        
        # 서버 이름
        grid.addWidget(self.create_label("서버 이름"), 0, 0)
        self.server_name = QLineEdit()
        self.server_name.setPlaceholderText("예: Production Server")
        if self.server_data:
            self.server_name.setText(self.server_data.get('name', ''))
        grid.addWidget(self.server_name, 1, 0)
        
        # IP 주소
        grid.addWidget(self.create_label("IP 주소"), 0, 1)
        self.ip_address = QLineEdit()
        self.ip_address.setPlaceholderText("192.168.1.100")
        if self.server_data:
            self.ip_address.setText(self.server_data.get('host', ''))
        grid.addWidget(self.ip_address, 1, 1)
        
        # 포트
        grid.addWidget(self.create_label("포트"), 2, 0)
        self.port = QLineEdit()
        self.port.setPlaceholderText("22")
        if self.server_data:
            self.port.setText(str(self.server_data.get('port', 22)))
        grid.addWidget(self.port, 3, 0)
        
        # 계정명
        grid.addWidget(self.create_label("계정명"), 2, 1)
        self.username = QLineEdit()
        self.username.setPlaceholderText("ubuntu")
        if self.server_data:
            self.username.setText(self.server_data.get('username', ''))
        grid.addWidget(self.username, 3, 1)
        
        # 비밀번호
        grid.addWidget(self.create_label("비밀번호 (선택)"), 4, 0)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("비밀번호 또는 SSH 키 사용")
        if self.server_data:
            self.password.setText(self.server_data.get('password', ''))
        grid.addWidget(self.password, 5, 0)
        
        # SSH 키 경로
        grid.addWidget(self.create_label("SSH 키 경로 (선택)"), 4, 1)
        self.key_path = QLineEdit()
        self.key_path.setPlaceholderText("~/.ssh/id_rsa")
        if self.server_data:
            self.key_path.setText(self.server_data.get('key_path', ''))
        grid.addWidget(self.key_path, 5, 1)
        
        layout.addLayout(grid)
    
    def create_tunnel_section(self, layout):
        """터널링 정보 섹션"""
        header_layout = QHBoxLayout()
        
        section_title = QLabel("터널링 정보")
        section_title.setObjectName("sectionTitle")
        header_layout.addWidget(section_title)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("+ 터널 추가")
        add_btn.setProperty("buttonStyle", "outline")
        add_btn.clicked.connect(self.add_tunnel_row)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # 터널 목록
        self.tunnel_container = QWidget()
        self.tunnel_layout = QVBoxLayout(self.tunnel_container)
        self.tunnel_layout.setSpacing(12)
        self.tunnel_layout.setContentsMargins(0, 0, 0, 0)
        
        # 기존 터널 로드
        if self.server_data and self.server_data.get('tunnels'):
            for tunnel in self.server_data['tunnels']:
                self.add_tunnel_row(tunnel)
        else:
            # 기본 터널 하나 추가
            self.add_tunnel_row()
        
        layout.addWidget(self.tunnel_container)
    
    def add_tunnel_row(self, tunnel_data=None):
        """터널 행 추가"""
        row = TunnelRow(tunnel_data, self)
        row.remove_clicked.connect(lambda: self.remove_tunnel_row(row))
        self.tunnel_rows.append(row)
        self.tunnel_layout.addWidget(row)
    
    def remove_tunnel_row(self, row):
        """터널 행 제거"""
        if len(self.tunnel_rows) > 1:
            self.tunnel_rows.remove(row)
            self.tunnel_layout.removeWidget(row)
            row.deleteLater()
    
    def create_footer_buttons(self, layout):
        """하단 버튼"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 취소 버튼
        cancel_btn = QPushButton("취소")
        cancel_btn.setProperty("buttonStyle", "outline")
        cancel_btn.setFixedWidth(120)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # 저장 버튼
        save_btn = QPushButton("✓ " + ("수정" if self.server_data else "추가"))
        save_btn.setFixedWidth(120)
        save_btn.clicked.connect(self.accept_form)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def accept_form(self):
        """폼 검증 및 저장"""
        # 필수 필드 검증
        if not self.server_name.text().strip():
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "입력 오류", "서버 이름을 입력하세요.")
            return
        
        if not self.ip_address.text().strip():
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "입력 오류", "IP 주소를 입력하세요.")
            return
        
        if not self.username.text().strip():
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "입력 오류", "계정명을 입력하세요.")
            return
        
        # 데이터 수집
        self.result_data = {
            'name': self.server_name.text().strip(),
            'host': self.ip_address.text().strip(),
            'port': int(self.port.text()) if self.port.text().strip() else 22,
            'username': self.username.text().strip(),
            'password': self.password.text(),
            'key_path': self.key_path.text().strip(),
            'tunnels': []
        }
        
        # 터널 데이터 수집
        for row in self.tunnel_rows:
            tunnel = row.get_data()
            if tunnel['local'] and tunnel['remote_port']:
                self.result_data['tunnels'].append(tunnel)
        
        self.accept()
    
    def create_label(self, text):
        """라벨 생성"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_SM};
            font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            color: {Theme.FOREGROUND};
        """)
        return label
    
    def get_dialog_stylesheet(self):
        """다이얼로그 스타일시트"""
        return f"""
            QDialog {{
                background-color: {Theme.BACKGROUND};
            }}
            
            #sectionTitle {{
                font-size: {Theme.FONT_SIZE_LG};
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.FOREGROUND};
            }}
            
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
                border: 1px solid {Theme.PRIMARY};
            }}
            
            QPushButton[buttonStyle="ghost"] {{
                background-color: transparent;
                border: none;
                color: {Theme.FOREGROUND};
            }}
            
            QPushButton[buttonStyle="ghost"]:hover {{
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 4px;
            }}
        """
    
    def get_result(self):
        """결과 데이터 반환"""
        return self.result_data

