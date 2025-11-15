# gui/add_server_dialog.py

import logging

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton,
    QFormLayout, QHBoxLayout, QMessageBox, QGroupBox, QFrame
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QFile, QIODevice
from core.encryption import encrypt_password  # 🔒 암호화 함수
from gui.icon_data import get_icon  # 내장된 아이콘 데이터 사용
from gui.theme import Theme
from gui.styled_message_box import StyledMessageBox

logger = logging.getLogger(__name__)

class AddServerDialog(QDialog):
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("서버 추가" if not existing_data else "서버 수정")
        self.setWindowIcon(get_icon())  # 내장된 아이콘 사용
        self.setFixedSize(520, 600)
        
        # Figma 디자인 스타일 적용
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BACKGROUND};
            }}
            QLabel {{
                color: {Theme.FOREGROUND};
                font-size: {Theme.FONT_SIZE_BASE};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            }}
            QLineEdit {{
                background-color: {Theme.CARD};
                border: 2px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} 12px;
                font-size: {Theme.FONT_SIZE_BASE};
                color: {Theme.FOREGROUND};
                min-height: 40px;
            }}
            QLineEdit:focus, QLineEdit:hover {{
                border: 2px solid {Theme.PRIMARY};
            }}
            QGroupBox {{
                background-color: {Theme.CARD};
                border: 2px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
                padding: {Theme.SPACING_LG};
                margin-top: 12px;
                font-size: {Theme.FONT_SIZE_LG};
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: {Theme.FOREGROUND};
            }}
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_FOREGROUND};
                border: 2px solid {Theme.PRIMARY};
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} {Theme.SPACING_LG};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: #1a1a2e;
                border: 2px solid #1a1a2e;
            }}
            QPushButton[buttonStyle="outline"] {{
                background-color: {Theme.CARD};
                color: {Theme.FOREGROUND};
                border: 2px solid {Theme.BORDER_SOLID};
            }}
            QPushButton[buttonStyle="outline"]:hover {{
                background-color: {Theme.ACCENT};
                border: 2px solid {Theme.PRIMARY};
            }}
            QPushButton[buttonStyle="destructive"] {{
                background-color: {Theme.CARD};
                color: {Theme.DESTRUCTIVE};
                border: 2px solid {Theme.DESTRUCTIVE};
                padding: 4px 12px;
                min-height: 36px;
            }}
            QPushButton[buttonStyle="destructive"]:hover {{
                background-color: {Theme.DESTRUCTIVE};
                color: {Theme.DESTRUCTIVE_FOREGROUND};
            }}
        """)

        # 기존 데이터를 먼저 저장
        self.server_data = existing_data.copy() if existing_data else None
        self.tunnel_rows = []  # 터널 행 리스트 초기화

        # 메인 레이아웃
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 다이얼로그 타이틀
        title_label = QLabel("서버 추가" if not existing_data else "서버 수정")
        title_label.setStyleSheet(f"""
            font-size: {Theme.FONT_SIZE_2XL};
            font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            color: {Theme.FOREGROUND};
            margin-bottom: 8px;
        """)
        layout.addWidget(title_label)

        # 서버 정보 입력 폼
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(0x0001 | 0x0080)  # Qt.AlignLeft | Qt.AlignVCenter
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("예: 개발 서버")
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("예: 192.168.1.100")
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("22")
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("예: ubuntu")
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("새 비밀번호를 입력하거나 비워두면 기존 비밀번호가 유지됩니다")

        form_layout.addRow("서버 이름", self.name_input)
        form_layout.addRow("IP 주소", self.host_input)
        form_layout.addRow("포트", self.port_input)
        form_layout.addRow("계정", self.username_input)
        form_layout.addRow("비밀번호", self.password_input)
        layout.addLayout(form_layout)

        # 터널링 입력 영역
        tunnel_box = QGroupBox("🔗 터널링 정보")
        self.tunnel_layout = QVBoxLayout()
        self.tunnel_layout.setSpacing(8)
        tunnel_box.setLayout(self.tunnel_layout)
        layout.addWidget(tunnel_box)

        # 기본 터널 행 추가 (기존 데이터가 없을 때만)
        if not existing_data:
            self.add_tunnel_row()

        self.add_tunnel_button = QPushButton("+ 포트포워딩 추가")
        self.add_tunnel_button.setProperty("buttonStyle", "outline")
        layout.addWidget(self.add_tunnel_button)

        layout.addStretch()

        # 저장/취소 버튼
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.cancel_button = QPushButton("취소")
        self.cancel_button.setProperty("buttonStyle", "outline")
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("저장")
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 기존 데이터가 있다면 불러오기
        if existing_data:
            self.load_existing_data(existing_data)

        # 이벤트 연결
        self.add_tunnel_button.clicked.connect(self.add_tunnel_row)
        self.save_button.clicked.connect(self.save)
        self.cancel_button.clicked.connect(self.reject)

    def add_tunnel_row(self, name="", local="", remote_host="", remote_port=""):
        if not isinstance(name, str): name = ""
        if not isinstance(local, str): local = ""
        if not isinstance(remote_host, str): remote_host = ""
        if not isinstance(remote_port, str): remote_port = ""

        logger.debug("터널 행 추가 시작: %d개 존재", len(self.tunnel_rows))

        # 위젯 생성 및 설정
        name_input = QLineEdit(name)
        local_input = QLineEdit(local)
        remote_host_input = QLineEdit(remote_host)
        remote_port_input = QLineEdit(remote_port)
        delete_button = QPushButton("✕")
        delete_button.setProperty("buttonStyle", "destructive")
        delete_button.setFixedWidth(44)

        # 플레이스홀더 설정
        name_input.setPlaceholderText("터널 이름")
        local_input.setPlaceholderText("로컬 포트")
        remote_host_input.setPlaceholderText("원격 호스트")
        remote_port_input.setPlaceholderText("원격 포트")

        row_widget = QFrame()
        row_widget.setObjectName("tunnelRowFrame")
        row_widget.setStyleSheet(f"""
            QFrame#tunnelRowFrame {{
                background-color: #f8fafc;
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: 12px;
            }}
        """)

        # 레이아웃 생성 및 위젯 추가
        row_layout = QHBoxLayout()
        row_layout.setSpacing(12)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(name_input, stretch=2)
        row_layout.addWidget(local_input, stretch=1)
        row_layout.addWidget(remote_host_input, stretch=2)
        row_layout.addWidget(remote_port_input, stretch=1)
        row_layout.addWidget(delete_button)
        row_widget.setLayout(row_layout)

        # 터널 행 정보 저장
        entry = {
            "name": name_input,
            "local": local_input,
            "remote_host": remote_host_input,
            "remote_port": remote_port_input,
            "container": row_widget
        }
        self.tunnel_rows.append(entry)
        logger.debug("터널 행 추가 완료: %d개 존재", len(self.tunnel_rows))

        def remove_row():
            logger.debug("터널 행 제거 시작: %d개 존재", len(self.tunnel_rows))
            if entry in self.tunnel_rows:
                self.tunnel_rows.remove(entry)
                logger.debug("터널 행 리스트에서 제거됨: %d개 남음", len(self.tunnel_rows))

                container = entry["container"]
                self.tunnel_layout.removeWidget(container)
                container.setParent(None)
                container.deleteLater()

                self.tunnel_layout.update()
                logger.debug("터널 행 제거 완료: %d개 존재", len(self.tunnel_rows))

        delete_button.clicked.connect(remove_row)
        self.tunnel_layout.addWidget(row_widget)

    def save(self):
        try:
            server_info = self._extract_server_inputs()
            password = self._resolve_password(server_info.pop("raw_password"))
            tunnels = self._collect_tunnels()

            self.server_data = {
                **server_info,
                "password": password,
                "tunnels": tunnels,
            }

            self.accept()

        except Exception as e:
            StyledMessageBox.critical(self, "입력 오류", str(e))

    def load_existing_data(self, data):
        self.name_input.setText(data['name'])
        self.host_input.setText(data['host'])
        self.port_input.setText(str(data.get('port', 22)))
        self.username_input.setText(data['username'])

        try:
            # 암호화된 비밀번호는 복호화 불가능 → 그대로 표시하지 않음
            self.password_input.setText("********")
        except:
            self.password_input.setText("")

        self._clear_tunnel_rows()

        for tunnel in data.get("tunnels", []):
            self.add_tunnel_row(
                name=tunnel.get("name", ""),
                local=str(tunnel.get("local", "")),
                remote_host=tunnel.get("remote_host", ""),
                remote_port=str(tunnel.get("remote_port", ""))
            )

    def _extract_server_inputs(self):
        name = self.name_input.text().strip()
        host = self.host_input.text().strip()
        username = self.username_input.text().strip()
        raw_password = self.password_input.text().strip()

        if not name or not host or not username:
            raise ValueError("필수 항목이 누락되었습니다.")

        try:
            port = int(self.port_input.text().strip() or 22)
        except ValueError:
            raise ValueError("포트 번호가 올바르지 않습니다.")

        return {
            "name": name,
            "host": host,
            "port": port,
            "username": username,
            "raw_password": raw_password,
        }

    def _resolve_password(self, raw_password):
        has_existing = self.server_data and "password" in self.server_data
        if raw_password == "********" and has_existing:
            return self.server_data["password"]
        if not raw_password and has_existing:
            return self.server_data["password"]
        if not raw_password:
            raise ValueError("비밀번호를 입력해주세요.")
        return encrypt_password(raw_password)

    def _collect_tunnels(self):
        tunnels = []
        logger.debug("터널 행 개수: %d", len(self.tunnel_rows))
        for idx, row in enumerate(self.tunnel_rows):
            t_name = row["name"].text().strip()
            local = row["local"].text().strip()
            remote_host = row["remote_host"].text().strip()
            remote_port = row["remote_port"].text().strip()

            logger.debug(
                "터널 %d 데이터 | 이름:%s 로컬:%s 원격:%s:%s",
                idx + 1,
                t_name,
                local,
                remote_host,
                remote_port,
            )

            if not (local and remote_host and remote_port):
                logger.debug("터널 %d 건너뜀: 필수 필드 누락", idx + 1)
                continue

            try:
                tunnels.append({
                    "name": t_name or "이름없음",
                    "local": int(local),
                    "remote_host": remote_host,
                    "remote_port": int(remote_port)
                })
                logger.debug("터널 %d 저장됨", idx + 1)
            except ValueError as e:
                logger.debug("터널 %d 오류: %s", idx + 1, str(e))
                raise ValueError(f"터널 {idx + 1}의 포트 번호가 올바르지 않습니다.")

        logger.debug("저장된 터널 개수: %d", len(tunnels))
        return tunnels

    def _clear_tunnel_rows(self):
        """모든 터널 입력 행 제거"""
        while self.tunnel_rows:
            entry = self.tunnel_rows.pop()
            container = entry.get("container")
            if container is not None:
                container.setParent(None)
                container.deleteLater()
