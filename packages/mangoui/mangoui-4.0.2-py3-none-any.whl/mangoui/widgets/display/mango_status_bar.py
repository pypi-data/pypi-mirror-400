# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 状态栏组件
# @Time   : 2025-11-25 11:10
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoStatusBar(QStatusBar):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QStatusBar {{
            background-color: {THEME.primary_100};
            border-top: 1px solid {THEME.primary_200};
            color: white;
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            padding: 4px;
        }}

        QStatusBar:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
            border-top: 1px solid {THEME.bg_300};
        }}

        QStatusBar QLabel {{
            color: white;
            background-color: transparent;
        }}

        QStatusBar QPushButton {{
            background-color: {THEME.primary_200};
            color: white;
            border: none;
            border-radius: {THEME.border_radius};
            padding: 4px 8px;
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}

        QStatusBar QPushButton:hover {{
            background-color: {THEME.primary_300};
        }}

        QStatusBar QPushButton:pressed {{
            background-color: {THEME.accent_100};
        }}

        QStatusBar QPushButton:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        """
        self.setStyleSheet(style)