# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoPushButton(QPushButton):
    def __init__(
            self,
            text,
            parent=None,
            **kwargs
    ):
        super().__init__()
        self.setText(text)
        self.kwargs = kwargs

        if parent:
            self.setParent(parent)

        self.set_stylesheet()
        self.setCursor(Qt.PointingHandCursor)  # type: ignore

    def set_stylesheet(self, height=36, width=60):
        # 获取按钮颜色，如果没有指定则使用主题主色
        button_color = self.kwargs.get('color', THEME.primary_100)
        
        style = f'''
        QPushButton {{
            border: none;
            color: white;
            border-radius: {THEME.border_radius};
            background-color: {button_color};
            padding: 8px 16px;
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            font-weight: 500;
            outline: none;
        }}
        QPushButton:hover {{
            background-color: {THEME.primary_200 if button_color == THEME.primary_100 else THEME.accent_200};
        }}
        QPushButton:pressed {{
            background-color: {THEME.primary_300 if button_color == THEME.primary_100 else THEME.bg_300};
        }}
        QPushButton:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        '''
        self.setStyleSheet(style)
        self.setMinimumHeight(height)
        self.setMinimumWidth(width)
