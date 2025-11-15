# main.py
# 프로그램 실행 진입점
# 여기서 GUI 어플리케이션을 시작함

import sys  # 시스템 관련 기능 (예: 프로그램 종료) 사용
from PyQt5.QtWidgets import QApplication  # PyQt 앱 실행에 필요한 기본 클래스
from gui.main_window import MainWindow  # 우리가 직접 만든 메인 GUI 창 불러오기

# 프로그램 실행을 위한 표준 코드 (모든 PyQt 앱은 이걸로 시작함)
if __name__ == "__main__":
    # QApplication 객체 생성 - 모든 PyQt 앱은 이게 있어야 함
    app = QApplication(sys.argv)

    # 메인 윈도우 인스턴스 생성
    window = MainWindow()
    window.show()  # 창 보여주기

    # 이벤트 루프 실행 (여기서부터 앱이 실제로 동작함)
    sys.exit(app.exec_())
