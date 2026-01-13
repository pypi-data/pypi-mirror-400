from PySide6.QtCore import QPropertyAnimation
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoMessage(QWidget):
    def __init__(self, parent, message, style):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)  # type: ignore
        self.setFixedHeight(30)
        self.setAttribute(Qt.WA_TranslucentBackground)  # type: ignore

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)  # type: ignore

        font_metrics = QFontMetrics(self.label.font())
        text_width = font_metrics.boundingRect(message).width()
        self.setFixedWidth(int(text_width * 1.5 if text_width < 110 else text_width * 1.3))

        self.layout.addStretch(1)
        self.layout.addWidget(self.label, 8)
        self.layout.addStretch(1)

        # 设置背景颜色和边框
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {style};
                border-radius: {THEME.border_radius};
                border: 1px solid {THEME.bg_300};
                padding: 8px 16px;
            }}
            
            QLabel {{
                color: {THEME.text_100};
                font-family: {THEME.font.family};
                font-size: {THEME.font.text_size}px;
                font-weight: 500;
            }}
        """)

        # 设置渐隐效果
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(1500)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.close)
        self.animation.start()

        self.hovered = False

    def enterEvent(self, event):
        """鼠标进入事件，暂停渐隐动画"""
        if not self.hovered:
            self.hovered = True
            self.animation.stop()

    def leaveEvent(self, event):
        """鼠标离开事件，重新开始渐隐动画"""
        if self.hovered:
            self.hovered = False
            self.animation.start()
