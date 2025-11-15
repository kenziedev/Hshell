# gui/components/header_bar.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
from gui.theme import Theme


class HeaderBar(QWidget):
    """
    상단 타이틀바 컴포넌트
    Figma 디자인: slate-800 배경에 Network 아이콘 + 앱명 + 설정 버튼
    """
    settings_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)  # 피그마 기준: 48px
        self.setObjectName("headerBar")
        
        # QPalette로 배경색 강제 설정 (최우선순위)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(Theme.TITLEBAR_BG))
        palette.setColor(QPalette.Base, QColor(Theme.TITLEBAR_BG))
        self.setPalette(palette)
        
        # 헤더바 전체와 자식 요소에 배경 강제 적용
        self.setStyleSheet(f"""
            QWidget#headerBar {{
                background: {Theme.TITLEBAR_BG};
                border: none;
                margin: 0;
                padding: 0;
            }}
            QWidget#headerBar QWidget {{
                background: {Theme.TITLEBAR_BG};
            }}
            QWidget#headerBar QLabel {{
                background: transparent;
            }}
        """)
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(10)
        
        # 왼쪽: 아이콘 + 앱명
        icon_label = QLabel("🌐")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(24, 24)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                padding: 0;
                margin: 0;
            }
        """)
        layout.addWidget(icon_label, alignment=Qt.AlignVCenter)
        
        # 앱 이름
        title_label = QLabel("Hshell")
        title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 15px;
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
                color: {Theme.TITLEBAR_TEXT};
                padding: 0;
                margin: 0;
                letter-spacing: 0.3px;
            }}
        """)
        layout.addWidget(title_label, alignment=Qt.AlignVCenter)
        
        layout.addStretch()
        
        # 오른쪽: 설정 버튼 (더 작고 날렵하게)
        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("settingsBtn")
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setFixedSize(32, 32)
        settings_btn.setStyleSheet(f"""
            QPushButton#settingsBtn {{
                background: transparent;
                border: none;
                border-radius: 4px;
                padding: 0;
                margin: 0;
                font-size: 16px;
                color: {Theme.TITLEBAR_TEXT};
            }}
            QPushButton#settingsBtn:hover {{
                background: {Theme.TITLEBAR_HOVER};
            }}
            QPushButton#settingsBtn:pressed {{
                background: #475569;
            }}
        """)
        settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(settings_btn, alignment=Qt.AlignVCenter)
        
        self.setLayout(layout)

