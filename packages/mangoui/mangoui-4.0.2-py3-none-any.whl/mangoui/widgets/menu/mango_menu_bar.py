# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 菜单栏组件
# @Time   : 2025-11-25 11:00
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoMenuBar(QMenuBar):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QMenuBar {{
            background-color: {THEME.primary_100};
            border-bottom: 1px solid {THEME.primary_200};
            color: white;
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: 8px 12px;
            border-radius: {THEME.border_radius};
        }}

        QMenuBar::item:selected {{
            background-color: {THEME.primary_200};
        }}

        QMenuBar::item:pressed {{
            background-color: {THEME.primary_300};
        }}

        QMenuBar::item:disabled {{
            color: {THEME.text_200};
        }}

        QMenuBar QMenu {{
            background-color: {THEME.bg_100};
            border: 1px solid {THEME.bg_300};
            border-radius: {THEME.border_radius};
            padding: 4px;
        }}

        QMenuBar QMenu::item {{
            padding: 8px 20px;
            background-color: transparent;
            color: {THEME.text_100};
        }}

        QMenuBar QMenu::item:selected {{
            background-color: {THEME.primary_100};
            color: white;
        }}

        QMenuBar QMenu::item:disabled {{
            color: {THEME.text_200};
        }}

        QMenuBar QMenu::separator {{
            height: 1px;
            background-color: {THEME.bg_300};
            margin: 4px 0;
        }}
        """
        self.setStyleSheet(style)