# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-01 下午9:53
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoNotification(QWidget):
    def __init__(self, parent, message, style):
        super().__init__(parent)
        self.style = style
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)  # type: ignore
        self.setFixedSize(240, 80)
        self.setObjectName("MangoNotification")
        self.setAttribute(Qt.WA_TranslucentBackground)  # type: ignore

        # 创建一个带圆角的 QFrame
        self.frame = QFrame(self)
        self.frame.setObjectName("notificationFrame")
        self.frame.setFixedSize(240, 80)
        self.frame.setFrameShape(QFrame.NoFrame)  # type: ignore
        self.frame.setStyleSheet(f"""
                   QFrame#notificationFrame {{
                       background-color: {self.style};
                       border-radius: 8px;
                   }}
               """)

        self.layout = QVBoxLayout(self.frame)
        self.layout.setContentsMargins(10, 0, 0, 0)
        self.layout.addWidget(QLabel(message))

        # 设置渐隐效果
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(2000)
        self.animation.setStartValue(2.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.close)
        self.animation.start()
        self.hovered = False

    def enterEvent(self, event):
        """鼠标进入事件，暂停渐隐动画"""
        if not self.hovered:
            self.hovered = True
            self.animation.stop()  # 停止动画

    def leaveEvent(self, event):
        """鼠标离开事件，重新开始渐隐动画"""
        if self.hovered:
            self.hovered = False
            self.animation.start()  # 重新开始动画
