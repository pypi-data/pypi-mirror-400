# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 单选按钮组件
# @Time   : 2025-11-25 10:10
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoRadioButton(QRadioButton):
    def __init__(self, text="", parent=None, **kwargs):
        super().__init__(text, parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QRadioButton {{
            spacing: 8px;
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}

        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
        }}

        QRadioButton::indicator:unchecked {{
            border: 2px solid {THEME.bg_300};
            border-radius: 9px;
            background-color: {THEME.bg_100};
        }}

        QRadioButton::indicator:unchecked:hover {{
            border: 2px solid {THEME.primary_200};
        }}

        QRadioButton::indicator:unchecked:pressed {{
            border: 2px solid {THEME.primary_300};
            background-color: {THEME.bg_200};
        }}

        QRadioButton::indicator:checked {{
            border: 2px solid {THEME.primary_100};
            border-radius: 9px;
            background-color: {THEME.primary_100};
            width: 18px;
            height: 18px;
        }}

        QRadioButton::indicator:checked:hover {{
            border: 2px solid {THEME.primary_200};
        }}

        QRadioButton::indicator:checked:pressed {{
            border: 2px solid {THEME.primary_300};
        }}

        QRadioButton:disabled {{
            color: {THEME.text_200};
        }}

        QRadioButton::indicator:disabled {{
            border: 2px solid {THEME.bg_200};
        }}

        QRadioButton::indicator:checked:disabled:after {{
            background-color: {THEME.text_200};
        }}
        """
        self.setStyleSheet(style)
        self.setMinimumHeight(30)