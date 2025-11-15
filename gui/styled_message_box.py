# gui/styled_message_box.py
"""
Figma 디자인 스타일이 적용된 메시지 박스
"""

from PyQt5.QtWidgets import QMessageBox
from gui.theme import Theme


class StyledMessageBox(QMessageBox):
    """Figma 디자인이 적용된 커스텀 메시지 박스"""
    
    @staticmethod
    def information(parent, title, text):
        """정보 메시지 박스"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {Theme.CARD};
            }}
            QMessageBox QLabel {{
                color: {Theme.FOREGROUND};
                font-size: {Theme.FONT_SIZE_BASE};
                min-width: 300px;
            }}
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_FOREGROUND};
                border: none;
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} {Theme.SPACING_LG};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                min-height: 36px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #1a1a2e;
            }}
        """)
        return msg.exec_()
    
    @staticmethod
    def warning(parent, title, text):
        """경고 메시지 박스"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {Theme.CARD};
            }}
            QMessageBox QLabel {{
                color: {Theme.FOREGROUND};
                font-size: {Theme.FONT_SIZE_BASE};
                min-width: 300px;
            }}
            QPushButton {{
                background-color: #f59e0b;
                color: #ffffff;
                border: none;
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} {Theme.SPACING_LG};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                min-height: 36px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #d97706;
            }}
        """)
        return msg.exec_()
    
    @staticmethod
    def critical(parent, title, text):
        """오류 메시지 박스"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {Theme.CARD};
            }}
            QMessageBox QLabel {{
                color: {Theme.FOREGROUND};
                font-size: {Theme.FONT_SIZE_BASE};
                min-width: 300px;
            }}
            QPushButton {{
                background-color: {Theme.DESTRUCTIVE};
                color: {Theme.DESTRUCTIVE_FOREGROUND};
                border: none;
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} {Theme.SPACING_LG};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                min-height: 36px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #b81636;
            }}
        """)
        return msg.exec_()
    
    @staticmethod
    def question(parent, title, text, buttons=QMessageBox.Yes | QMessageBox.No):
        """질문 메시지 박스"""
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(buttons)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {Theme.CARD};
            }}
            QMessageBox QLabel {{
                color: {Theme.FOREGROUND};
                font-size: {Theme.FONT_SIZE_BASE};
                min-width: 300px;
            }}
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_FOREGROUND};
                border: none;
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM} {Theme.SPACING_LG};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                min-height: 36px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #1a1a2e;
            }}
            QPushButton[text="&No"], QPushButton[text="아니오"] {{
                background-color: transparent;
                color: {Theme.FOREGROUND};
                border: 1px solid {Theme.BORDER_SOLID};
            }}
            QPushButton[text="&No"]:hover, QPushButton[text="아니오"]:hover {{
                background-color: {Theme.ACCENT};
            }}
        """)
        return msg.exec_()

