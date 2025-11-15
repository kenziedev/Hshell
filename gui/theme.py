# gui/theme.py
"""
Figma 디자인 시스템 토큰을 PyQt5 스타일로 변환
피그마 Make 디자인과 정확히 일치하도록 업데이트
"""

class Theme:
    # ===== 색상 토큰 (Figma globals.css 기반) =====
    # Light mode colors
    BACKGROUND = "#f1f5f9"  # slate-100 (피그마 App.tsx)
    FOREGROUND = "#0a0a0a"
    CARD = "#ffffff"
    CARD_FOREGROUND = "#0a0a0a"
    
    PRIMARY = "#030213"
    PRIMARY_FOREGROUND = "#ffffff"
    
    SECONDARY = "#f1f5f9"  # slate-50
    SECONDARY_FOREGROUND = "#030213"
    
    MUTED = "#ececf0"
    MUTED_FOREGROUND = "#717182"
    
    ACCENT = "#e9ebef"
    ACCENT_FOREGROUND = "#030213"
    
    DESTRUCTIVE = "#d4183d"
    DESTRUCTIVE_FOREGROUND = "#ffffff"
    
    BORDER = "rgba(0, 0, 0, 0.1)"
    BORDER_SOLID = "#e2e8f0"  # slate-200
    
    INPUT_BACKGROUND = "#f3f3f5"
    SWITCH_BACKGROUND = "#cbced4"
    
    # Title bar colors (피그마 App.tsx의 slate-800)
    TITLEBAR_BG = "#1e293b"  # slate-800
    TITLEBAR_TEXT = "#ffffff"
    TITLEBAR_HOVER = "#334155"  # slate-700
    
    # Status colors
    STATUS_ACTIVE_BG = "#dcfce7"  # green-100
    STATUS_ACTIVE_TEXT = "#166534"  # green-800
    STATUS_INACTIVE_BG = "#f3f4f6"  # gray-100
    STATUS_INACTIVE_TEXT = "#6b7280"  # gray-500
    
    # ===== 타이포그래피 =====
    FONT_FAMILY = "Segoe UI, Noto Sans KR, sans-serif"
    FONT_SIZE_BASE = "14px"
    FONT_SIZE_SM = "13px"
    FONT_SIZE_LG = "16px"
    FONT_SIZE_XL = "18px"
    FONT_SIZE_2XL = "22px"
    
    FONT_WEIGHT_NORMAL = "400"
    FONT_WEIGHT_MEDIUM = "500"
    FONT_WEIGHT_SEMIBOLD = "600"
    
    # ===== 간격 및 크기 =====
    RADIUS = "10px"
    RADIUS_SM = "6px"
    RADIUS_MD = "8px"
    RADIUS_LG = "10px"
    RADIUS_XL = "14px"
    
    SPACING_XS = "4px"
    SPACING_SM = "8px"
    SPACING_MD = "12px"
    SPACING_LG = "16px"
    SPACING_XL = "24px"
    SPACING_2XL = "32px"
    
    # ===== 그림자 =====
    SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
    SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)"
    
    @staticmethod
    def get_global_stylesheet():
        """전역 QSS 스타일시트 반환"""
        return f"""
            /* ===== 전역 기본 스타일 ===== */
            QWidget {{
                font-family: {Theme.FONT_FAMILY};
                font-size: {Theme.FONT_SIZE_BASE};
                color: {Theme.FOREGROUND};
            }}
            
            QMainWindow {{
                background-color: {Theme.BACKGROUND};
            }}
            
            /* ===== 버튼 스타일 (피그마 Button variants 기반) ===== */
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: {Theme.PRIMARY_FOREGROUND};
                border: none;
                border-radius: {Theme.RADIUS_MD};
                padding: 8px 16px;
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
                font-size: {Theme.FONT_SIZE_SM};
                min-height: 36px;
                transition: all 0.2s ease;
            }}
            
            QPushButton:hover {{
                background-color: #1a1a2e;
            }}
            
            QPushButton:pressed {{
                background-color: #0f0f1e;
            }}
            
            QPushButton:disabled {{
                background-color: {Theme.MUTED};
                color: {Theme.MUTED_FOREGROUND};
                opacity: 0.5;
            }}
            
            QPushButton[buttonStyle="outline"] {{
                background-color: transparent;
                color: {Theme.FOREGROUND};
                border: 1px solid {Theme.BORDER_SOLID};
            }}
            
            QPushButton[buttonStyle="outline"]:hover {{
                background-color: {Theme.ACCENT};
                color: {Theme.ACCENT_FOREGROUND};
            }}
            
            QPushButton[buttonStyle="secondary"] {{
                background-color: {Theme.SECONDARY};
                color: {Theme.SECONDARY_FOREGROUND};
                border: none;
            }}
            
            QPushButton[buttonStyle="secondary"]:hover {{
                background-color: #e2e8f0;
            }}
            
            QPushButton[buttonStyle="ghost"] {{
                background-color: transparent;
                color: {Theme.FOREGROUND};
                border: none;
            }}
            
            QPushButton[buttonStyle="ghost"]:hover {{
                background-color: {Theme.ACCENT};
                color: {Theme.ACCENT_FOREGROUND};
            }}
            
            QPushButton[buttonStyle="destructive"] {{
                background-color: {Theme.DESTRUCTIVE};
                color: {Theme.DESTRUCTIVE_FOREGROUND};
                border: none;
            }}
            
            QPushButton[buttonStyle="destructive"]:hover {{
                background-color: #b81636;
            }}
            
            /* ===== 입력 필드 (피그마 Input 스타일) ===== */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {Theme.INPUT_BACKGROUND};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: 8px 12px;
                color: {Theme.FOREGROUND};
                font-size: {Theme.FONT_SIZE_BASE};
                font-weight: {Theme.FONT_WEIGHT_NORMAL};
                selection-background-color: {Theme.PRIMARY};
                selection-color: {Theme.PRIMARY_FOREGROUND};
                min-height: 36px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {Theme.PRIMARY};
                background-color: {Theme.CARD};
                outline: 3px solid rgba(3, 2, 19, 0.1);
            }}
            
            QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
                border: 1px solid {Theme.PRIMARY};
            }}
            
            QLineEdit::placeholder, QTextEdit::placeholder, QPlainTextEdit::placeholder {{
                color: {Theme.MUTED_FOREGROUND};
            }}
            
            /* ===== 리스트 위젯 ===== */
            QListWidget {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_SM};
                outline: none;
            }}
            
            QListWidget::item {{
                border-radius: {Theme.RADIUS_SM};
                padding: {Theme.SPACING_MD};
                margin: 2px 0px;
            }}
            
            QListWidget::item:hover {{
                background-color: {Theme.ACCENT};
            }}
            
            QListWidget::item:selected {{
                background-color: {Theme.SECONDARY};
                color: {Theme.SECONDARY_FOREGROUND};
                border: 1px solid {Theme.PRIMARY};
            }}
            
            /* ===== 스크롤바 ===== */
            QScrollBar:vertical {{
                border: none;
                background: {Theme.MUTED};
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {Theme.MUTED_FOREGROUND};
                border-radius: 5px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {Theme.PRIMARY};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background: {Theme.MUTED};
                height: 10px;
                border-radius: 5px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {Theme.MUTED_FOREGROUND};
                border-radius: 5px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background: {Theme.PRIMARY};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            /* ===== 탭 위젯 (피그마 Tabs 스타일) ===== */
            QTabWidget::pane {{
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
                background-color: {Theme.CARD};
                padding: 4px;
            }}
            
            QTabBar::tab {{
                background-color: transparent;
                color: {Theme.MUTED_FOREGROUND};
                border: none;
                border-radius: {Theme.RADIUS_SM};
                padding: {Theme.SPACING_SM} {Theme.SPACING_LG};
                margin-right: 4px;
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            }}
            
            QTabBar::tab:selected {{
                background-color: {Theme.CARD};
                color: {Theme.FOREGROUND};
                border: 1px solid {Theme.BORDER_SOLID};
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {Theme.ACCENT};
                color: {Theme.ACCENT_FOREGROUND};
            }}
            
            /* ===== 레이블 ===== */
            QLabel {{
                color: {Theme.FOREGROUND};
                background-color: transparent;
            }}
            
            QLabel[labelStyle="title"] {{
                font-size: {Theme.FONT_SIZE_XL};
                font-weight: {Theme.FONT_WEIGHT_SEMIBOLD};
            }}
            
            QLabel[labelStyle="muted"] {{
                color: {Theme.MUTED_FOREGROUND};
                font-size: {Theme.FONT_SIZE_SM};
            }}
            
            /* ===== 카드 스타일 프레임 ===== */
            QFrame[frameStyle="card"] {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_LG};
            }}
            
            QFrame[frameStyle="titlebar"] {{
                background-color: {Theme.TITLEBAR_BG};
                border: none;
            }}
            
            /* ===== 메시지 박스 ===== */
            QMessageBox {{
                background-color: {Theme.CARD};
            }}
            
            QMessageBox QLabel {{
                color: {Theme.FOREGROUND};
            }}
            
            /* ===== 다이얼로그 ===== */
            QDialog {{
                background-color: {Theme.CARD};
            }}
        """
    
    @staticmethod
    def get_titlebar_stylesheet():
        """타이틀바 전용 스타일"""
        return f"""
            QWidget {{
                background-color: {Theme.TITLEBAR_BG};
                color: {Theme.TITLEBAR_TEXT};
            }}
            
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: {Theme.RADIUS_SM};
                padding: {Theme.SPACING_SM};
                min-width: 32px;
                min-height: 32px;
            }}
            
            QPushButton:hover {{
                background-color: {Theme.TITLEBAR_HOVER};
            }}
            
            QLabel {{
                color: {Theme.TITLEBAR_TEXT};
                font-weight: {Theme.FONT_WEIGHT_MEDIUM};
            }}
        """
    
    @staticmethod
    def get_log_stylesheet():
        """로그 영역 전용 스타일"""
        return f"""
            QTextEdit {{
                background-color: {Theme.CARD};
                border: 1px solid {Theme.BORDER_SOLID};
                border-radius: {Theme.RADIUS_MD};
                padding: {Theme.SPACING_MD};
                font-family: Consolas, Monaco, monospace;
                font-size: {Theme.FONT_SIZE_SM};
                color: {Theme.FOREGROUND};
            }}
        """

