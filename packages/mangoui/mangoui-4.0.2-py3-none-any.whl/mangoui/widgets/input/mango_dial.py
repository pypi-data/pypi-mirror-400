# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 刻度盘组件
# @Time   : 2025-11-25 10:35
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoDial(QDial):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.setNotchesVisible(True)
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QDial {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
        }}

        QDial::handle {{
            background-color: {THEME.primary_100};
            border: 2px solid {THEME.primary_200};
            border-radius: 4px;
            width: 16px;
            height: 16px;
        }}

        QDial::handle:hover {{
            background-color: {THEME.primary_200};
        }}

        QDial::handle:pressed {{
            background-color: {THEME.primary_300};
        }}

        QDial:disabled {{
            background-color: {THEME.bg_200};
        }}

        QDial::handle:disabled {{
            background-color: {THEME.text_200};
            border: 2px solid {THEME.bg_300};
        }}
        """
        self.setStyleSheet(style)