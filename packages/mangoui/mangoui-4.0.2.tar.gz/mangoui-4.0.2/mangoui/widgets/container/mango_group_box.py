# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 分组框组件
# @Time   : 2025-11-25 10:45
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoGroupBox(QGroupBox):
    def __init__(self, title="", parent=None, **kwargs):
        super().__init__(title, parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QGroupBox {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            margin-top: 1ex;
            font-family: {THEME.font.family};
            font-size: {THEME.font.title_size}px;
            font-weight: bold;
            color: {THEME.text_100};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            background-color: {THEME.bg_100};
        }}

        QGroupBox:disabled {{
            color: {THEME.text_200};
            border: 1px solid {THEME.bg_200};
        }}

        QGroupBox::title:disabled {{
            color: {THEME.text_200};
        }}
        """
        self.setStyleSheet(style)