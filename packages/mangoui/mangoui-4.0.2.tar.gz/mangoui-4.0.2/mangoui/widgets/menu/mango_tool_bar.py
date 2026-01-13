# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 工具栏组件
# @Time   : 2025-11-25 11:05
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoToolBar(QToolBar):
    def __init__(self, title="", parent=None, **kwargs):
        super().__init__(title, parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QToolBar {{
            background-color: {THEME.bg_100};
            border: 1px solid {THEME.bg_300};
            border-radius: {THEME.border_radius};
            padding: 4px;
            spacing: 4px;
        }}

        QToolBar:disabled {{
            background-color: {THEME.bg_200};
        }}

        QToolBar QToolButton {{
            background-color: {THEME.bg_100};
            border: 1px solid {THEME.bg_300};
            border-radius: {THEME.border_radius};
            padding: 6px 10px;
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}

        QToolBar QToolButton:hover {{
            background-color: {THEME.bg_200};
            border: 1px solid {THEME.primary_100};
        }}

        QToolBar QToolButton:pressed {{
            background-color: {THEME.primary_100};
            color: white;
        }}

        QToolBar QToolButton:checked {{
            background-color: {THEME.primary_200};
            color: white;
        }}

        QToolBar QToolButton:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}

        QToolBar::separator {{
            width: 1px;
            background-color: {THEME.bg_300};
            margin: 2px;
        }}

        QToolBar::handle {{
            background-color: {THEME.bg_300};
            border: 1px solid {THEME.bg_200};
            border-radius: 2px;
        }}
        """
        self.setStyleSheet(style)