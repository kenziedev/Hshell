from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QFont, QTextCursor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from gui.theme import Theme
import pyte
import time

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

class SSHTerminalWidget(QWidget):
    def __init__(self, ssh_manager, parent=None):
        super().__init__(parent)
        
        self.ssh_manager = ssh_manager
        self.channel = None
        self.output_thread = None
        self._last_render = ""
        
        # Pyte 화면 구성
        self.screen = pyte.Screen(80, 24)
        self.stream = pyte.Stream(self.screen)

        # 텍스트 표시용 위젯
        self.text_area = QTextEdit()
        self.text_area.setFont(QFont("Consolas, Monaco, monospace", 11))
        self.text_area.setReadOnly(False)
        self.text_area.setTextInteractionFlags(Qt.TextEditorInteraction)
        
        # Figma 디자인 스타일 적용
        self.text_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: #1a1a1a;
                color: #10b981;
                border: none;
                border-radius: {Theme.RADIUS_SM};
                padding: {Theme.SPACING_MD};
                font-family: Consolas, Monaco, monospace;
                font-size: 13px;
                selection-background-color: #334155;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 여백 제거
        layout.addWidget(self.text_area)
        self.setLayout(layout)

        # 키보드 입력 이벤트 연결
        self.text_area.installEventFilter(self)

        # SSH 채널 초기화
        self.initialize_channel()

        # 화면 주기적 갱신 (렌더링)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_screen)
        self.refresh_timer.start(100)

        # 터미널 재연결 감시 타이머
        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.timeout.connect(self.check_connection)
        self.reconnect_timer.start(10000)

    def initialize_channel(self):
        """SSH 채널을 초기화하고 출력 스레드를 시작합니다."""
        self._stop_output_thread()
        if self.ssh_manager and self.ssh_manager.is_connected():
            self.channel = self.ssh_manager.client.invoke_shell()
            self.output_thread = OutputThread(self.channel)
            self.output_thread.data_received.connect(self.handle_data)
            self.output_thread.start()
            self._last_render = ""

    def handle_data(self, data):
        try:
            decoded = data.decode("utf-8", errors="replace")
            self.stream.feed(decoded)
        except Exception as e:
            print(f"[pyte decode error] {e}")

    def update_screen(self):
        content = "\n".join(self.screen.display)
        if content == self._last_render:
            return
        self._last_render = content
        cursor = self.text_area.textCursor()
        self.text_area.blockSignals(True)
        self.text_area.setPlainText(content)
        self.text_area.blockSignals(False)
        cursor.movePosition(QTextCursor.End)
        self.text_area.setTextCursor(cursor)

    def eventFilter(self, source, event):
        if source == self.text_area and event.type() == event.KeyPress:
            if not self.channel:
                return True

            key = event.key()
            text = event.text()

            if key == Qt.Key_Backspace:
                self.channel.send('\x7f')
            elif key == Qt.Key_Return or key == Qt.Key_Enter:
                self.channel.send('\n')
            elif text:
                self.channel.send(text)

            return True
        return super().eventFilter(source, event)

    def check_connection(self):
        """연결 상태를 확인하고 필요한 경우 재연결을 시도합니다."""
        if not self.ssh_manager or not self.ssh_manager.is_connected():
            self._stop_output_thread()
            if self.channel:
                self.channel.close()
                self.channel = None

            try:
                if self.ssh_manager.connect():
                    self.initialize_channel()
                    self.screen.reset()
                    self.stream = pyte.Stream(self.screen)
                    self._last_render = ""
                    self.append_system_message("[ 재연결 성공 ]\n")
                else:
                    self.append_system_message("[ 재연결 실패 - 연결 종료 ]\n")
                    self.parent().close()  # 탭 닫기
            except Exception as e:
                self.append_system_message(f"[ 재연결 오류: {e} ]\n")
                self.parent().close()  # 탭 닫기

    def append_system_message(self, message):
        self.text_area.moveCursor(QTextCursor.End)
        self.text_area.insertPlainText(message)
        self.text_area.moveCursor(QTextCursor.End)

    def close_connection(self):
        """연결을 정리하고 리소스를 해제합니다."""
        self._stop_output_thread()
        if self.channel:
            self.channel.close()
        self.refresh_timer.stop()
        self.reconnect_timer.stop()

    def _stop_output_thread(self):
        if self.output_thread:
            self.output_thread.stop()
            self.output_thread.wait(1)
            self.output_thread = None