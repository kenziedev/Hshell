# gui/components/server_form_card.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QLineEdit, QFrame, QGridLayout, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from gui.theme import Theme
import logging

logger = logging.getLogger(__name__)


class TunnelRow(QWidget):
    """터널 입력 행 컴포넌트"""
    remove_clicked = pyqtSignal()
    
    def __init__(self, tunnel_data=None, parent=None):
        super().__init__(parent)
        self.tunnel_data = tunnel_data or {}
        self.init_ui()
    
    def init_ui(self):
        # 피그마 TunnelManager의 터널 입력 행 스타일 (slate-50 배경)
        self.setObjectName("tunnelRow")
        self.setStyleSheet(f"""
            QWidget#tunnelRow {{
                background-color: #f8fafc;
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
            }}
        """)
        
        layout = QHBoxLayout()
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
        
        # 호스트
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
        delete_btn.setFixedSize(36, 36)
        delete_btn.clicked.connect(self.remove_clicked.emit)
        layout.addWidget(delete_btn)
        
        self.setLayout(layout)
    
    def get_data(self):
        """터널 데이터 반환"""
        return {
            'name': self.tunnel_name.text().strip(),
            'local': self.local_port.text().strip(),
            'remote_host': self.remote_host.text().strip(),
            'remote_port': self.remote_port.text().strip()
        }


class ServerFormCard(QWidget):
    """
    서버 추가/수정 폼 카드 컴포넌트
    Figma 디자인: 인라인 확장 폼
    """
    save_clicked = pyqtSignal(dict)
    cancel_clicked = pyqtSignal()
    
    def __init__(self, server_data=None, parent=None):
        super().__init__(parent)
        self.server_data = server_data
        self.tunnel_rows = []
        self.init_ui()
    
    def init_ui(self):
        # 피그마 TunnelManager 폼 카드 스타일
        self.setObjectName("serverFormCard")
        self.setStyleSheet(f"""
            QWidget#serverFormCard {{
                background-color: {Theme.CARD};
                border: 2px solid {Theme.PRIMARY};
                border-radius: {Theme.RADIUS_LG};
            }}
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        # 헤더 (피그마 CardTitle 스타일)
        header_layout = QHBoxLayout()
        title = QLabel("✏️ 서버 설정 수정" if self.server_data else "➕ 새 서버 설정")
        title.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_XL};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
            background-color: transparent;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        # 서버 정보 섹션
        server_section = QVBoxLayout()
        server_section.setSpacing(16)
        
        section_title = QLabel("서버 정보")
        section_title.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_LG};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
            background-color: transparent;
        """)
        server_section.addWidget(section_title)
        
        # 그리드 레이아웃 (2열)
        grid = QGridLayout()
        grid.setSpacing(12)
        
        # 첫 번째 줄: 서버 이름, IP 주소
        grid.addWidget(self.create_label("서버 이름"), 0, 0)
        self.server_name = QLineEdit()
        self.server_name.setPlaceholderText("예: Production Server")
        if self.server_data:
            self.server_name.setText(self.server_data.get('name', ''))
        grid.addWidget(self.server_name, 1, 0)
        
        grid.addWidget(self.create_label("IP 주소"), 0, 1)
        self.ip_address = QLineEdit()
        self.ip_address.setPlaceholderText("192.168.1.100")
        if self.server_data:
            self.ip_address.setText(self.server_data.get('host', ''))
        grid.addWidget(self.ip_address, 1, 1)
        
        # 두 번째 줄: 포트, 계정명, 비밀번호
        grid.addWidget(self.create_label("포트"), 2, 0, 1, 1)
        self.port = QLineEdit()
        self.port.setPlaceholderText("22")
        if self.server_data:
            self.port.setText(str(self.server_data.get('port', 22)))
        grid.addWidget(self.port, 3, 0, 1, 1)
        
        # 계정명과 비밀번호를 오른쪽에 배치
        right_grid = QGridLayout()
        right_grid.setSpacing(12)
        
        right_grid.addWidget(self.create_label("계정명"), 0, 0)
        self.username = QLineEdit()
        self.username.setPlaceholderText("admin")
        if self.server_data:
            self.username.setText(self.server_data.get('username', ''))
        right_grid.addWidget(self.username, 1, 0)
        
        right_grid.addWidget(self.create_label("비밀번호"), 0, 1)
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("••••••••")
        if self.server_data:
            self.password.setText("********")
        right_grid.addWidget(self.password, 1, 1)
        
        grid.addLayout(right_grid, 3, 1)
        
        server_section.addLayout(grid)
        main_layout.addLayout(server_section)
        
        # 구분선
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: {Theme.BORDER_SOLID}; max-height: 1px;")
        main_layout.addWidget(separator)
        
        # 터널링 정보 섹션
        tunnel_section = QVBoxLayout()
        tunnel_section.setSpacing(12)
        
        tunnel_header = QHBoxLayout()
        tunnel_title = QLabel("터널링 정보")
        tunnel_title.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_LG};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
            background-color: transparent;
        """)
        tunnel_header.addWidget(tunnel_title)
        tunnel_header.addStretch()
        
        add_tunnel_btn = QPushButton("+ 터널 추가")
        add_tunnel_btn.setProperty("buttonStyle", "outline")
        add_tunnel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.CARD};
                color: {Theme.FOREGROUND};
                border: 2px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} {Theme.SPACING_MD};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                font-size: {Theme.FONT_SIZE_SM};
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT};
                border: 2px solid {Theme.PRIMARY};
            }}
        """)
        add_tunnel_btn.clicked.connect(self.add_tunnel_row)
        tunnel_header.addWidget(add_tunnel_btn)
        
        tunnel_section.addLayout(tunnel_header)
        
        # 터널 레이블 행
        label_layout = QHBoxLayout()
        label_layout.setSpacing(12)
        label_layout.setContentsMargins(12, 0, 12, 0)
        label_layout.addWidget(self.create_small_label("터널명"), stretch=2)
        label_layout.addWidget(self.create_small_label("로컬 포트"), stretch=1)
        label_layout.addWidget(self.create_small_label("호스트"), stretch=2)
        label_layout.addWidget(self.create_small_label("원격 포트"), stretch=1)
        label_layout.addSpacing(36)  # 삭제 버튼 공간
        tunnel_section.addLayout(label_layout)
        
        # 터널 행 컨테이너
        self.tunnel_container = QVBoxLayout()
        self.tunnel_container.setSpacing(8)
        tunnel_section.addLayout(self.tunnel_container)
        
        # 기존 터널 로드 또는 빈 행 추가
        if self.server_data and self.server_data.get('tunnels'):
            for tunnel in self.server_data['tunnels']:
                self.add_tunnel_row(tunnel)
        else:
            self.add_tunnel_row()
        
        main_layout.addLayout(tunnel_section)
        main_layout.addStretch()
        
        # 버튼 영역 (피그마 스타일)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        save_btn = QPushButton("✓ " + ("수정" if self.server_data else "추가"))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_FOREGROUND};
                border: 2px solid {Theme.PRIMARY};
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} {Theme.SPACING_XL};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                min-height: 44px;
                font-size: {Theme.FONT_SIZE_BASE};
            }}
            QPushButton:hover {{
                background-color: #1a1a2e;
                border: 2px solid #1a1a2e;
            }}
        """)
        save_btn.clicked.connect(self.on_save)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("취소")
        cancel_btn.setProperty("buttonStyle", "outline")
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.CARD};
                color: {Theme.FOREGROUND};
                border: 2px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} {Theme.SPACING_XL};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                min-height: 44px;
                font-size: {Theme.FONT_SIZE_BASE};
            }}
            QPushButton:hover {{
                background-color: {Theme.ACCENT};
                border: 2px solid {Theme.PRIMARY};
            }}
        """)
        cancel_btn.clicked.connect(self.cancel_clicked.emit)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def create_label(self, text):
        """입력 필드 레이블 생성 (피그마 Label 스타일)"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_BASE};
            font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            color: {Theme.FOREGROUND};
            background-color: transparent;
        """)
        return label
    
    def create_small_label(self, text):
        """작은 레이블 생성"""
        label = QLabel(text)
        label.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_SM};
            color: {Theme.MUTED_FOREGROUND};
        """)
        return label
    
    def add_tunnel_row(self, tunnel_data=None):
        """터널 행 추가"""
        row = TunnelRow(tunnel_data)
        row.remove_clicked.connect(lambda: self.remove_tunnel_row(row))
        self.tunnel_rows.append(row)
        self.tunnel_container.addWidget(row)
    
    def remove_tunnel_row(self, row):
        """터널 행 제거"""
        if len(self.tunnel_rows) > 1:
            self.tunnel_rows.remove(row)
            self.tunnel_container.removeWidget(row)
            row.deleteLater()
    
    def on_save(self):
        """저장 버튼 클릭"""
        try:
            # 터널 데이터 수집
            tunnels = []
            for row in self.tunnel_rows:
                data = row.get_data()
                if data['local'] and data['remote_host'] and data['remote_port']:
                    try:
                        tunnels.append({
                            'name': data['name'] or '이름없음',
                            'local': int(data['local']),
                            'remote_host': data['remote_host'],
                            'remote_port': int(data['remote_port'])
                        })
                    except ValueError:
                        from gui.styled_message_box import StyledMessageBox
                        StyledMessageBox.critical(self, "입력 오류", "포트 번호는 숫자여야 합니다.")
                        return
            
            # 비밀번호 처리
            password_text = self.password.text().strip()
            if password_text == "********" and self.server_data:
                password = self.server_data.get('password', '')
            elif password_text:
                from core.encryption import encrypt_password
                password = encrypt_password(password_text)
            elif self.server_data and self.server_data.get('password'):
                password = self.server_data['password']
            else:
                from gui.styled_message_box import StyledMessageBox
                StyledMessageBox.critical(self, "입력 오류", "비밀번호를 입력해주세요.")
                return
            
            # 서버 데이터 구성
            server_data = {
                'name': self.server_name.text().strip(),
                'host': self.ip_address.text().strip(),
                'port': int(self.port.text().strip() or 22),
                'username': self.username.text().strip(),
                'password': password,
                'tunnels': tunnels
            }
            
            if not all([server_data['name'], server_data['host'], server_data['username']]):
                from gui.styled_message_box import StyledMessageBox
                StyledMessageBox.critical(self, "입력 오류", "필수 항목을 모두 입력해주세요.")
                return
            
            self.save_clicked.emit(server_data)
            
        except ValueError:
            from gui.styled_message_box import StyledMessageBox
            StyledMessageBox.critical(self, "입력 오류", "포트 번호는 숫자여야 합니다.")
        except Exception as e:
            from gui.styled_message_box import StyledMessageBox
            StyledMessageBox.critical(self, "오류", str(e))

