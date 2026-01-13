# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 线性进度条组件
# @Time   : 2025-11-25 11:25
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoProgressBar(QProgressBar):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QProgressBar {{
            background-color: {THEME.bg_300};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            text-align: center;
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}

        QProgressBar::chunk {{
            background-color: {THEME.primary_100};
            border-radius: {THEME.border_radius};
        }}

        QProgressBar::chunk:hover {{
            background-color: {THEME.primary_200};
        }}

        QProgressBar:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}

        QProgressBar::chunk:disabled {{
            background-color: {THEME.text_200};
        }}
        """
        self.setStyleSheet(style)
        self.setMinimumHeight(20)