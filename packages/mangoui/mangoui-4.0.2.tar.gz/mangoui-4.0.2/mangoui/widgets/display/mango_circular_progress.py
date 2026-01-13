# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏
from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QPainter, QFont, Qt, QPen
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect

from mangoui.settings.settings import THEME


class MangoCircularProgress(QWidget):
    def __init__(self,
                 parent,
                 value=0,
                 progress_width=10,
                 is_rounded=True,
                 max_value=100,
                 progress_color=THEME.primary_200,
                 enable_text=True,
                 font_family="微软雅黑",
                 font_size=12,
                 suffix="%",
                 text_color=THEME.text_100,
                 enable_bg=True,
                 bg_color=THEME.primary_300,
                 *args,
                 **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.value = value
        self.progress_width = progress_width
        self.progress_rounded_cap = is_rounded
        self.max_value = max_value
        self.progress_color = progress_color
        self.enable_text = enable_text
        self.font_family = font_family
        self.font_size = font_size
        self.suffix = suffix
        self.text_color = text_color
        self.enable_bg = enable_bg
        self.bg_color = bg_color

    def add_shadow(self, enable):
        if enable:
            self.shadow = QGraphicsDropShadowEffect(self)
            self.shadow.setBlurRadius(15)
            self.shadow.setXOffset(0)
            self.shadow.setYOffset(0)
            self.shadow.setColor(QColor(0, 0, 0, 80))
            self.setGraphicsEffect(self.shadow)

    def set_value(self, value):
        self.value = value
        self.repaint()

    def paintEvent(self, e):
        width = self.width() - self.progress_width
        height = self.height() - self.progress_width
        margin = self.progress_width / 2
        value = self.value * 360 / self.max_value

        paint = QPainter()
        if not paint.begin(self):
            return
        paint.setRenderHint(QPainter.Antialiasing)  # type: ignore
        paint.setFont(QFont(self.font_family, self.font_size))

        rect = QRect(0, 0, self.width(), self.height())
        paint.setPen(Qt.NoPen)  # type: ignore

        # 绘制背景圆环
        if self.enable_bg:
            pen = QPen()
            pen.setWidth(self.progress_width)
            pen.setColor(QColor(self.bg_color))
            if self.progress_rounded_cap:
                pen.setCapStyle(Qt.RoundCap)  # type: ignore
            paint.setPen(pen)
            paint.drawArc(int(margin), int(margin), int(width), int(height), 0, 360 * 16)  # type: ignore

        # 绘制进度圆环
        pen = QPen()
        pen.setWidth(self.progress_width)
        pen.setColor(QColor(self.progress_color))
        if self.progress_rounded_cap:
            pen.setCapStyle(Qt.RoundCap)  # type: ignore
        paint.setPen(pen)
        paint.drawArc(int(margin), int(margin), int(width), int(height), -90 * 16, -int(value * 16))  # type: ignore

        # 绘制中心文本
        if self.enable_text:
            # 添加阴影效果
            text_rect = QRect(int(margin), int(margin), int(width), int(height))
            # 绘制阴影
            shadow_pen = QPen()
            shadow_pen.setColor(QColor(0, 0, 0, 30))  # 半透明黑色阴影
            paint.setPen(shadow_pen)
            paint.drawText(text_rect, Qt.AlignCenter, f"{self.value}{self.suffix}")  # type: ignore
            
            # 绘制主文本
            pen.setColor(QColor(self.text_color))
            paint.setPen(pen)
            paint.drawText(rect, Qt.AlignCenter, f"{self.value}{self.suffix}")  # type: ignore

        paint.end()
