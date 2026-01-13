# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 列表控件组件
# @Time   : 2025-11-25 10:20
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoListWidget(QListWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QListWidget {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            outline: none;
            padding: 2px;
        }}

        QListWidget::item {{
            padding: 8px 12px;
            border-radius: {THEME.border_radius};
        }}

        QListWidget::item:selected {{
            background-color: {THEME.primary_100};
            color: white;
        }}

        QListWidget::item:hover {{
            background-color: {THEME.bg_200};
        }}

        QListWidget:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        """
        self.setStyleSheet(style)