# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-19 11:29
# @Author : 毛鹏
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoCard(QWidget):
    # 卡片组件
    clicked = Signal(str)

    def __init__(self, layout, title: str | None = None, parent=None, name='', **kwargs):
        super().__init__(parent)
        self.name = name  # 唯一标识
        self.kwargs = kwargs
        
        # 设置主布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(6, 6, 6, 6)  # 为阴影留出空间
        self.main_layout.setSpacing(0)
        
        # 创建卡片框架
        self.card_frame = QFrame()
        self.card_frame.setObjectName("cardFrame")
        
        # 设置卡片框架布局
        self.card_layout = QVBoxLayout(self.card_frame)
        self.card_layout.setContentsMargins(16, 16, 16, 16)  # 设置内边距
        self.card_layout.setSpacing(4)  # 移除布局间距效果
        
        # 如果有标题，添加标题
        if title:
            self.title_label = QLabel(title)
            self.title_label.setStyleSheet("background-color: transparent; border: none;")  # 确保标题背景透明
            font = QFont()
            font.setPointSize(14)  # 设置字体大小
            font.setBold(True)  # 设置为粗体
            self.title_label.setFont(font)
            self.card_layout.addWidget(self.title_label)
        
        # 添加内容布局
        if layout:
            layout.setContentsMargins(0, 0, 0, 0)
            # 检查布局是否已经有父级，如果有则不能直接添加
            if layout.parent() is None:
                self.card_layout.addLayout(layout)
            else:
                # 如果布局已经有父级，创建一个新的布局并复制内容
                # 或者直接使用 setLayout 而不是 addLayout
                pass
        
        # 将卡片框架添加到主布局
        self.main_layout.addWidget(self.card_frame)
        self.setLayout(self.main_layout)
        
        # 设置样式
        self.set_stylesheet()

    def paintEvent(self, event):
        """重写paintEvent方法来绘制阴影效果"""
        # 先调用父类的paintEvent
        super().paintEvent(event)
        
        # 检查 card_frame 是否存在且有效
        if not hasattr(self, 'card_frame') or not self.card_frame:
            return
        
        # 创建 QPainter 对象
        painter = QPainter(self)
        if not painter.isActive():
            return
        painter.setRenderHint(QPainter.Antialiasing)  # 抗锯齿
        
        # 获取卡片框架的几何信息
        rect = self.card_frame.geometry()
        if rect.width() <= 0 or rect.height() <= 0:
            return
        
        # 创建阴影效果 - 绘制多层半透明矩形来模拟阴影
        for i in range(3):
            shadow_color = QColor(0, 0, 0, 15 - i * 5)  # 逐渐减小透明度
            painter.setPen(Qt.NoPen)
            painter.setBrush(shadow_color)
            shadow_rect = QRect(rect.x() + i, rect.y() + i, rect.width(), rect.height())
            painter.drawRoundedRect(shadow_rect, 8, 8)

    def enterEvent(self, event):
        if self.name:
            self.setCursor(Qt.PointingHandCursor)  # type: ignore
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        if self.name:
            self.setCursor(Qt.ArrowCursor)  # type: ignore
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # type: ignore
            self.clicked.emit(self.name)  # 发送点击信号
        super().mousePressEvent(event)  # 确保调用父类方法

    def get_background_color(self):
        """获取背景颜色"""
        background_color = self.kwargs.get('background_color')
        if background_color is None:
            background_color = '#F2F3F5'  # 使用浅灰色作为默认背景色
        return background_color

    def set_stylesheet(self):
        self.setObjectName('mangoCard')
        
        style = f"""
        QWidget#mangoCard {{
            background-color: transparent;
            border: none;
            padding: 0px;
        }}
        
        QFrame#cardFrame {{
            background-color: {self.get_background_color()};
            border: 1px solid {THEME.bg_300};
            border-radius: {THEME.border_radius};
        }}
        
        QWidget#mangoCard:hover QFrame#cardFrame {{
            border: 1px solid {THEME.primary_200};
        }}
        
        QLabel {{
            background-color: transparent;  /* 确保标签背景透明 */
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}
        """
        self.setStyleSheet(style)
        
    def setContentsMargins(self, left, top, right, bottom):
        """重写setContentsMargins方法，确保卡片框架也有正确的边距"""
        super().setContentsMargins(left, top, right, bottom)
        if hasattr(self, 'card_layout'):
            self.card_layout.setContentsMargins(16, 16, 16, 16)