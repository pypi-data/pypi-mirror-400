# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 工具箱组件
# @Time   : 2025-11-25 10:55
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoToolBox(QToolBox):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QToolBox {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}

        QToolBox::tab {{
            background-color: {THEME.primary_100};
            border: 1px solid {THEME.primary_200};
            color: white;
            padding: 8px 12px;
        }}

        QToolBox::tab:selected {{
            background-color: {THEME.primary_200};
            border: 1px solid {THEME.primary_300};
        }}

        QToolBox::tab:hover {{
            background-color: {THEME.primary_200};
        }}

        QToolBox::tab:selected:hover {{
            background-color: {THEME.primary_300};
        }}

        QToolBox::tab:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
            border: 1px solid {THEME.bg_300};
        }}

        QToolBox QScrollArea {{
            background-color: {THEME.bg_100};
            border: none;
        }}
        """
        self.setStyleSheet(style)