# gui/main_window.py

from PyQt5.QtWidgets import (
    QDialog, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QHBoxLayout, QMessageBox, QTextEdit
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QFile, QIODevice
from core.tunnel_config import load_server_list, save_server_list
from core.ssh_manager import SSHManager
from gui.add_server_dialog import AddServerDialog
from gui.ssh_terminal_dialog import SSHTerminalDialog  # 🔥 콘솔 다이얼로그 임포트
from gui.icon_data import get_icon  # 내장된 아이콘 데이터 사용

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(get_icon())  # 내장된 아이콘 사용

        self.ssh_managers = {}  # 서버별 SSH 매니저 저장 {index: SSHManager}
        self.connected_indices = set()  # 연결된 서버 인덱스 집합

        self.setWindowTitle("Hshell")
        self.setGeometry(100, 100, 1000, 700)  # 창 크기 약간 키움

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 메인 레이아웃을 수평으로 분할
        main_layout = QHBoxLayout()
        
        # 왼쪽 패널 (기존 위젯들)
        left_panel = QVBoxLayout()
        self.title_label = QLabel("서버 목록")
        left_panel.addWidget(self.title_label)

        self.server_list = QListWidget()
        left_panel.addWidget(self.server_list)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        left_panel.addWidget(self.detail_text)

        # 버튼들
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("서버 추가")
        self.edit_button = QPushButton("서버 수정")
        self.delete_button = QPushButton("서버 삭제")
        self.connect_button = QPushButton("ON")
        self.disconnect_button = QPushButton("OFF")
        self.ssh_button = QPushButton("SSH")

        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.edit_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.connect_button)
        self.button_layout.addWidget(self.disconnect_button)
        self.button_layout.addWidget(self.ssh_button)

        left_panel.addLayout(self.button_layout)
        
        # 오른쪽 패널 (로그 메시지)
        right_panel = QVBoxLayout()
        log_label = QLabel("로그 메시지")
        right_panel.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumWidth(300)  # 최소 너비 설정
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                font-family: Consolas, monospace;
                font-size: 9pt;
            }
        """)
        right_panel.addWidget(self.log_text)
        
        # 패널들을 메인 레이아웃에 추가
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        main_layout.addWidget(left_widget, stretch=7)  # 왼쪽 패널이 더 넓게
        main_layout.addWidget(right_widget, stretch=3)  # 오른쪽 패널은 좁게
        
        self.central_widget.setLayout(main_layout)

        # 서버 목록 불러오기
        self.servers = load_server_list()
        self.refresh_server_list()

        # 버튼 동작 연결
        self.add_button.clicked.connect(self.add_server)
        self.edit_button.clicked.connect(self.edit_server)
        self.delete_button.clicked.connect(self.delete_server)
        self.connect_button.clicked.connect(self.connect_server)
        self.disconnect_button.clicked.connect(self.disconnect_server)
        self.ssh_button.clicked.connect(self.open_ssh_console)

        self.server_list.currentRowChanged.connect(self.show_server_detail)
        
        # 초기 로그 메시지
        self.log_message("프로그램이 시작되었습니다.")

    def log_message(self, message, level="info"):
        """
        로그 메시지를 추가합니다.
        level: "info", "success", "warning", "error"
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 레벨에 따른 색상 설정
        color = {
            "info": "#000000",      # 검정
            "success": "#008000",   # 초록
            "warning": "#FFA500",   # 주황
            "error": "#FF0000"      # 빨강
        }.get(level, "#000000")
        
        # HTML 형식으로 메시지 추가
        formatted_message = f'<span style="color: {color}">[{timestamp}] {message}</span>'
        self.log_text.append(formatted_message)
        
        # 스크롤을 항상 아래로
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def refresh_server_list(self):
        selected = self.server_list.currentRow()
        self.server_list.clear()

        for i, server in enumerate(self.servers):
            name = server['name']
            if i in self.connected_indices:  # 연결된 서버 체크
                name += " [연결됨]"
            self.server_list.addItem(name)

        if selected >= 0 and selected < self.server_list.count():
            self.server_list.setCurrentRow(selected)

    def show_server_detail(self, index):
        if index < 0 or index >= len(self.servers):
            self.detail_text.clear()
            return

        server = self.servers[index]
        details = f"▶ 서버 이름: {server['name']}\n"
        details += f"▶ 호스트: {server['host']}:{server['port']}\n"
        details += f"▶ 사용자: {server['username']}\n"
        details += f"▶ 터널링:\n"

        if server.get("tunnels"):
            for tunnel in server["tunnels"]:
                details += f"   - [{tunnel.get('name', '이름없음')}] "
                details += f"Local:{tunnel['local']} → {tunnel['remote_host']}:{tunnel['remote_port']}\n"
        else:
            details += "   (없음)\n"

        self.detail_text.setText(details)

    def add_server(self):
        dialog = AddServerDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_server = dialog.server_data
            self.servers.append(new_server)
            save_server_list(self.servers)
            self.refresh_server_list()
            self.log_message(f"{new_server['name']} 서버가 추가되었습니다.", "success")

    def connect_server(self):
        index = self.server_list.currentRow()
        if index < 0 or index >= len(self.servers):
            self.log_message("서버를 먼저 선택하세요.", "warning")
            return

        if index in self.connected_indices:
            self.log_message(f"{self.servers[index]['name']} 서버는 이미 연결되어 있습니다.", "warning")
            return

        server_info = self.servers[index]
        ssh_manager = SSHManager(server_info)

        self.log_message(f"{server_info['name']} 서버 연결 시도 중...", "info")
        success = ssh_manager.connect()
        
        if success:
            self.ssh_managers[index] = ssh_manager
            self.connected_indices.add(index)
            self.refresh_server_list()
            self.show_server_detail(index)
            self.log_message(f"{server_info['name']} 서버에 연결되었습니다.", "success")
        else:
            self.log_message(f"{server_info['name']} 서버 연결에 실패했습니다.", "error")

    def disconnect_server(self):
        index = self.server_list.currentRow()
        if index < 0 or index >= len(self.servers):
            self.log_message("연결을 해제할 서버를 선택하세요.", "warning")
            return

        if index not in self.connected_indices:
            self.log_message(f"{self.servers[index]['name']} 서버는 연결되어 있지 않습니다.", "warning")
            return

        if index in self.ssh_managers:
            self.ssh_managers[index].disconnect()
            del self.ssh_managers[index]
            self.connected_indices.remove(index)
            self.refresh_server_list()
            self.log_message(f"{self.servers[index]['name']} 서버 연결이 종료되었습니다.", "info")

    def edit_server(self):
        index = self.server_list.currentRow()
        if index < 0 or index >= len(self.servers):
            self.log_message("수정할 서버를 먼저 선택하세요.", "warning")
            return

        current_data = self.servers[index]
        dialog = AddServerDialog(self, existing_data=current_data)
        if dialog.exec_() == QDialog.Accepted:
            self.servers[index] = dialog.server_data
            save_server_list(self.servers)
            self.refresh_server_list()
            self.log_message(f"{dialog.server_data['name']} 서버 정보가 수정되었습니다.", "success")

    def delete_server(self):
        index = self.server_list.currentRow()
        if index < 0 or index >= len(self.servers):
            self.log_message("삭제할 서버를 먼저 선택하세요.", "warning")
            return

        name = self.servers[index]['name']
        confirm = QMessageBox.question(self, "삭제 확인", f"{name} 서버를 삭제할까요?",
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
            self.detail_text.clear()
            self.log_message(f"{name} 서버가 삭제되었습니다.", "info")

    def open_ssh_console(self):
        index = self.server_list.currentRow()
        if index < 0 or index >= len(self.servers):
            self.log_message("서버를 먼저 선택하세요.", "warning")
            return

        if index not in self.connected_indices or index not in self.ssh_managers:
            self.log_message("먼저 서버에 연결하세요.", "warning")
            return

        self.log_message(f"{self.servers[index]['name']} 서버의 SSH 콘솔을 엽니다.", "info")
        dialog = SSHTerminalDialog(self.ssh_managers[index], self)
        dialog.exec_()
