# gui/ssh_terminal_dialog.py

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QFont, QTextCursor, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QFile, QIODevice
from gui.icon_data import get_icon  # 내장된 아이콘 데이터 사용

import pyte
import time
import os, sys

class OutputThread(QThread):
    data_received = pyqtSignal(bytes)

    def __init__(self, channel):
        super().__init__()
        self.channel = channel
        self._running = True

    def run(self):
        while self._running:
            if self.channel.recv_ready():
                data = self.channel.recv(1024)
                self.data_received.emit(data)
            time.sleep(0.02)

    def stop(self):
        self._running = False


class SSHTerminalDialog(QDialog):
    def __init__(self, ssh_manager, parent=None):
        super().__init__(parent)
        
        self.ssh_manager = ssh_manager
        server_name = self.ssh_manager.server_info.get("name", "알 수 없음")
        self.setWindowTitle(f"Hshell 터미널 ({server_name})")
        self.setMinimumSize(800, 500)

        # Pyte 화면 구성
        self.screen = pyte.Screen(80, 24)
        self.stream = pyte.Stream(self.screen)

        self.ssh_manager = ssh_manager
        self.channel = self.ssh_manager.client.invoke_shell()

        # 텍스트 표시용 위젯
        self.text_area = QTextEdit()
        self.text_area.setFont(QFont("Courier", 10))
        self.text_area.setReadOnly(False)
        self.text_area.setTextInteractionFlags(Qt.TextEditorInteraction)

        layout = QVBoxLayout()
        layout.addWidget(self.text_area)
        self.setLayout(layout)

        # 키보드 입력 이벤트 연결
        self.text_area.installEventFilter(self)

        # 수신 쓰레드 시작
        self.output_thread = OutputThread(self.channel)
        self.output_thread.data_received.connect(self.handle_data)
        self.output_thread.start()

        # 화면 주기적 갱신 (렌더링)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_screen)
        self.refresh_timer.start(100)

        # 터미널 재연결 감시 타이머
        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.timeout.connect(self.check_connection)
        self.reconnect_timer.start(10000)

        self.setWindowIcon(get_icon())  # 내장된 아이콘 사용

    def handle_data(self, data):
        try:
            decoded = data.decode("utf-8", errors="replace")
            self.stream.feed(decoded)
        except Exception as e:
            print(f"[pyte decode error] {e}")

    def update_screen(self):
        content = "\n".join(self.screen.display)
        self.text_area.setPlainText(content)
        self.text_area.moveCursor(self.text_area.textCursor().End)

    def eventFilter(self, source, event):
        if source == self.text_area and event.type() == event.KeyPress:
            key = event.key()
            text = event.text()

            if key == Qt.Key_Backspace:
                self.channel.send('\x7f')  # 대부분의 셸에서 DEL 인식
            elif key == Qt.Key_Return or key == Qt.Key_Enter:
                self.channel.send('\n')
            elif text:
                self.channel.send(text)

            return True
        return super().eventFilter(source, event)

    def closeEvent(self, event):
        self.output_thread.stop()
        self.channel.close()
        self.refresh_timer.stop()
        event.accept()

    def check_connection(self):
        if not self.ssh_manager or not self.ssh_manager.is_connected():
            self.output_thread.stop()
            self.channel.close()

            try:
                if self.ssh_manager.connect():  # 🔁 재연결 시도
                    self.channel = self.ssh_manager.client.invoke_shell()
                    self.screen.reset()
                    self.stream = pyte.Stream(self.screen)

                    self.output_thread = OutputThread(self.channel)
                    self.output_thread.data_received.connect(self.handle_data)
                    self.output_thread.start()

                    self.append_system_message("[ 재연결 성공 ]\n")
                else:
                    self.append_system_message("[ 재연결 실패 - 연결 종료 ]\n")
                    self.close()

            except Exception as e:
                self.append_system_message(f"[ 재연결 오류: {e} ]\n")

    def append_system_message(self, message):
        self.text_area.moveCursor(QTextCursor.End)
        self.text_area.insertPlainText(message)
        self.text_area.moveCursor(QTextCursor.End)