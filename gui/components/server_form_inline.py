# gui/components/server_form_inline.py
"""
인라인 서버 추가/수정 폼 (피그마처럼 메인 화면 안에 표시)
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from gui.theme import Theme


class TunnelRowInline(QWidget):
    """터널 입력 행 (인라인)"""
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
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 8, 12, 8)
        
        # 터널명
        self.tunnel_name = QLineEdit(self.tunnel_data.get('name', ''))
        self.tunnel_name.setPlaceholderText("터널 이름")
        layout.addWidget(self.tunnel_name, stretch=2)
        
        # 로컬 포트
        self.local_port = QLineEdit(str(self.tunnel_data.get('local', '')))
        self.local_port.setPlaceholderText("로컬")
        layout.addWidget(self.local_port, stretch=1)
        
        # 원격 호스트
        self.remote_host = QLineEdit(self.tunnel_data.get('remote_host', ''))
        self.remote_host.setPlaceholderText("원격 호스트")
        layout.addWidget(self.remote_host, stretch=2)
        
        # 원격 포트
        self.remote_port = QLineEdit(str(self.tunnel_data.get('remote_port', '')))
        self.remote_port.setPlaceholderText("원격")
        layout.addWidget(self.remote_port, stretch=1)
        
        # 삭제 버튼
        delete_btn = QPushButton("✕")
        delete_btn.setObjectName("tunnelDeleteBtn")
        delete_btn.setFixedSize(28, 28)
        delete_btn.setCursor(Qt.PointingHandCursor)
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


class ServerFormInline(QFrame):
    """인라인 서버 폼 (메인 화면에 통합)"""
    save_clicked = pyqtSignal(dict)  # 저장된 데이터 전달
    cancel_clicked = pyqtSignal()
    
    def __init__(self, server_data=None, parent=None):
        super().__init__(parent)
        self.server_data = server_data
        self.tunnel_rows = []
        self.setObjectName("serverFormInline")
        self.init_ui()
    
    def init_ui(self):
        self.setStyleSheet(f"""
            QFrame#serverFormInline {{
                background-color: {Theme.CARD};
                border: 2px solid {Theme.PRIMARY};
                border-radius: {Theme.RADIUS_LG};
            }}
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(20)
        
        # 헤더
        header_layout = QHBoxLayout()
        title = QLabel("✏️ 서버 설정 수정" if self.server_data else "➕ 새 서버 추가")
        title.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_XL};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
            background: transparent;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # 서버 정보 섹션
        self.create_server_section(main_layout)
        
        # 터널링 정보 섹션
        self.create_tunnel_section(main_layout)
        
        # 하단 버튼
        self.create_footer_buttons(main_layout)
    
    def create_server_section(self, layout):
        """서버 정보 섹션"""
        section_title = QLabel("📡 서버 정보")
        section_title.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_BASE};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
            background: transparent;
        """)
        layout.addWidget(section_title)
        
        grid = QGridLayout()
        grid.setSpacing(12)
        
        # 서버 이름
        self.server_name = QLineEdit()
        self.server_name.setPlaceholderText("서버 이름 (예: Production Server)")
        if self.server_data:
            self.server_name.setText(self.server_data.get('name', ''))
        grid.addWidget(self.server_name, 0, 0, 1, 2)
        
        # IP 주소
        self.ip_address = QLineEdit()
        self.ip_address.setPlaceholderText("IP 주소")
        if self.server_data:
            self.ip_address.setText(self.server_data.get('host', ''))
        grid.addWidget(self.ip_address, 1, 0)
        
        # 포트
        self.port = QLineEdit()
        self.port.setPlaceholderText("포트 (기본: 22)")
        if self.server_data:
            self.port.setText(str(self.server_data.get('port', 22)))
        grid.addWidget(self.port, 1, 1)
        
        # 계정명
        self.username = QLineEdit()
        self.username.setPlaceholderText("계정명")
        if self.server_data:
            self.username.setText(self.server_data.get('username', ''))
        grid.addWidget(self.username, 2, 0)
        
        # 비밀번호
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("비밀번호 (선택)")
        if self.server_data:
            self.password.setText(self.server_data.get('password', ''))
        grid.addWidget(self.password, 2, 1)
        
        # SSH 키 경로
        self.key_path = QLineEdit()
        self.key_path.setPlaceholderText("SSH 키 경로 (선택, 예: ~/.ssh/id_rsa)")
        if self.server_data:
            self.key_path.setText(self.server_data.get('key_path', ''))
        grid.addWidget(self.key_path, 3, 0, 1, 2)
        
        layout.addLayout(grid)
    
    def create_tunnel_section(self, layout):
        """터널링 정보 섹션"""
        header_layout = QHBoxLayout()
        
        section_title = QLabel("🔗 터널링 정보")
        section_title.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_BASE};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
            background: transparent;
        """)
        header_layout.addWidget(section_title)
        
        header_layout.addStretch()
        
        add_btn = QPushButton("+ 터널 추가")
        add_btn.setProperty("buttonStyle", "outline")
        add_btn.setFixedHeight(32)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_tunnel_row)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # 터널 목록
        self.tunnel_container = QWidget()
        self.tunnel_container.setStyleSheet("background: transparent;")
        self.tunnel_layout = QVBoxLayout(self.tunnel_container)
        self.tunnel_layout.setSpacing(8)
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
        row = TunnelRowInline(tunnel_data, self)
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
        
        # 취소 버튼
        cancel_btn = QPushButton("취소")
        cancel_btn.setProperty("buttonStyle", "outline")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.cancel_clicked.emit)
        button_layout.addWidget(cancel_btn)
        
        # 저장 버튼
        save_btn = QPushButton("✓ " + ("수정" if self.server_data else "추가"))
        save_btn.setFixedHeight(40)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_form)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def save_form(self):
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
        result_data = {
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
                result_data['tunnels'].append(tunnel)
        
        self.save_clicked.emit(result_data)

