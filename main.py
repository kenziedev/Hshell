# main.py

import sys
import logging
from PyQt5.QtWidgets import QApplication
from gui.main_window_v2 import MainWindow

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Hshell")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
