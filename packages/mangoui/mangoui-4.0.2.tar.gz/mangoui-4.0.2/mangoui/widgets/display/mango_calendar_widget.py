# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 日历控件组件
# @Time   : 2025-11-25 11:20
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoCalendarWidget(QCalendarWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QCalendarWidget {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
        }}

        QCalendarWidget QToolButton {{
            background-color: {THEME.primary_100};
            color: white;
            border: none;
            border-radius: {THEME.border_radius};
            padding: 4px;
            font-weight: bold;
        }}

        QCalendarWidget QToolButton:hover {{
            background-color: {THEME.primary_200};
        }}

        QCalendarWidget QToolButton:pressed {{
            background-color: {THEME.primary_300};
        }}

        QCalendarWidget QToolButton:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}

        QCalendarWidget QMenu {{
            background-color: {THEME.bg_100};
            border: 1px solid {THEME.bg_300};
            border-radius: {THEME.border_radius};
        }}

        QCalendarWidget QMenu::item {{
            padding: 4px 12px;
            background-color: transparent;
            color: {THEME.text_100};
        }}

        QCalendarWidget QMenu::item:selected {{
            background-color: {THEME.primary_100};
            color: white;
        }}

        QCalendarWidget QMenu::item:disabled {{
            color: {THEME.text_200};
        }}

        QCalendarWidget QWidget {{
            alternate-background-color: {THEME.bg_200};
        }}

        QCalendarWidget QAbstractItemView:enabled {{
            font-size: {THEME.font.text_size}px;
            color: {THEME.text_100};
            background-color: {THEME.bg_100};
            selection-background-color: {THEME.primary_100};
            selection-color: white;
        }}

        QCalendarWidget QAbstractItemView:disabled {{
            color: {THEME.text_200};
        }}

        QCalendarWidget QAbstractItemView:selected {{
            background-color: {THEME.primary_100};
            color: white;
        }}
        """
        self.setStyleSheet(style)