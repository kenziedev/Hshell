# gui/add_server_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton,
    QFormLayout, QHBoxLayout, QMessageBox, QGroupBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QFile, QIODevice
from core.encryption import encrypt_password  # 🔒 암호화 함수
from gui.icon_data import get_icon  # 내장된 아이콘 데이터 사용

class AddServerDialog(QDialog):
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("서버 추가" if not existing_data else "서버 수정")
        self.setWindowIcon(get_icon())  # 내장된 아이콘 사용
        self.setFixedSize(450, 500)

        self.server_data = None
        self.tunnel_rows = []  # 터널 행 리스트 초기화

        # 메인 레이아웃
        layout = QVBoxLayout()

        # 서버 정보 입력 폼
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.host_input = QLineEdit()
        self.port_input = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()

        form_layout.addRow("서버 이름", self.name_input)
        form_layout.addRow("IP 주소", self.host_input)
        form_layout.addRow("포트 (기본 22)", self.port_input)
        form_layout.addRow("계정", self.username_input)
        form_layout.addRow("비밀번호", self.password_input)
        layout.addLayout(form_layout)

        # 터널링 입력 영역
        tunnel_box = QGroupBox("터널링 정보")
        self.tunnel_layout = QVBoxLayout()
        tunnel_box.setLayout(self.tunnel_layout)
        layout.addWidget(tunnel_box)

        # 기본 터널 행 추가 (기존 데이터가 없을 때만)
        if not existing_data:
            self.add_tunnel_row()

        self.add_tunnel_button = QPushButton("포트포워딩 추가")
        layout.addWidget(self.add_tunnel_button)

        # 저장/취소 버튼
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("저장")
        self.cancel_button = QPushButton("취소")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
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

        print(f"터널 행 추가 시작: {len(self.tunnel_rows)}개 존재")  # 디버그 로그

        # 위젯 생성 및 설정
        name_input = QLineEdit(name)
        local_input = QLineEdit(local)
        remote_host_input = QLineEdit(remote_host)
        remote_port_input = QLineEdit(remote_port)
        delete_button = QPushButton("삭제")

        # 플레이스홀더 설정
        name_input.setPlaceholderText("이름")
        local_input.setPlaceholderText("로컬 포트")
        remote_host_input.setPlaceholderText("원격 IP")
        remote_port_input.setPlaceholderText("원격 포트")

        # 레이아웃 생성 및 위젯 추가
        row_layout = QHBoxLayout()
        row_layout.addWidget(name_input)
        row_layout.addWidget(local_input)
        row_layout.addWidget(remote_host_input)
        row_layout.addWidget(remote_port_input)
        row_layout.addWidget(delete_button)

        # 터널 행 정보 저장
        entry = (name_input, local_input, remote_host_input, remote_port_input, row_layout)
        self.tunnel_rows.append(entry)
        print(f"터널 행 추가 완료: {len(self.tunnel_rows)}개 존재")  # 디버그 로그

        def remove_row():
            print(f"터널 행 제거 시작: {len(self.tunnel_rows)}개 존재")  # 디버그 로그
            if entry in self.tunnel_rows:
                self.tunnel_rows.remove(entry)
                print(f"터널 행 리스트에서 제거됨: {len(self.tunnel_rows)}개 남음")  # 디버그 로그

                # 위젯들 제거
                for widget in entry[:4]:
                    if widget is not None:
                        widget.setParent(None)
                        widget.deleteLater()
                if delete_button is not None:
                    delete_button.setParent(None)
                    delete_button.deleteLater()

                # 레이아웃 정리
                self.tunnel_layout.removeItem(row_layout)
                row_layout.setParent(None)
                row_layout.deleteLater()

                self.tunnel_layout.update()
                print(f"터널 행 제거 완료: {len(self.tunnel_rows)}개 존재")  # 디버그 로그

        delete_button.clicked.connect(remove_row)
        self.tunnel_layout.addLayout(row_layout)

    def save(self):
        try:
            name = self.name_input.text().strip()
            host = self.host_input.text().strip()
            port = int(self.port_input.text().strip() or 22)
            username = self.username_input.text().strip()
            raw_password = self.password_input.text().strip()
            password = encrypt_password(raw_password)  # 🔐 암호화

            if not name or not host or not username or not raw_password:
                raise ValueError("필수 항목이 누락되었습니다.")

            tunnels = []
            print(f"터널 행 개수: {len(self.tunnel_rows)}")  # 디버그 로그
            for idx, row in enumerate(self.tunnel_rows):
                t_name = row[0].text().strip()
                local = row[1].text().strip()
                remote_host = row[2].text().strip()
                remote_port = row[3].text().strip()

                print(f"터널 {idx + 1} 데이터:")  # 디버그 로그
                print(f"  이름: {t_name}")
                print(f"  로컬: {local}")
                print(f"  원격호스트: {remote_host}")
                print(f"  원격포트: {remote_port}")

                if not (local and remote_host and remote_port):
                    print(f"  터널 {idx + 1} 건너뜀: 필수 필드 누락")  # 디버그 로그
                    continue

                try:
                    tunnels.append({
                        "name": t_name or "이름없음",
                        "local": int(local),
                        "remote_host": remote_host,
                        "remote_port": int(remote_port)
                    })
                    print(f"  터널 {idx + 1} 저장됨")  # 디버그 로그
                except ValueError as e:
                    print(f"  터널 {idx + 1} 오류: {str(e)}")  # 디버그 로그
                    raise ValueError(f"터널 {idx + 1}의 포트 번호가 올바르지 않습니다.")

            print(f"저장된 터널 개수: {len(tunnels)}")  # 디버그 로그

            self.server_data = {
                "name": name,
                "host": host,
                "port": port,
                "username": username,
                "password": password,
                "tunnels": tunnels
            }

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "입력 오류", str(e))

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

        for i in range(len(self.tunnel_rows)):
            for widget in self.tunnel_rows[i]:
                widget.deleteLater()
        self.tunnel_rows.clear()

        for tunnel in data.get("tunnels", []):
            self.add_tunnel_row(
                name=tunnel.get("name", ""),
                local=str(tunnel.get("local", "")),
                remote_host=tunnel.get("remote_host", ""),
                remote_port=str(tunnel.get("remote_port", ""))
            )
