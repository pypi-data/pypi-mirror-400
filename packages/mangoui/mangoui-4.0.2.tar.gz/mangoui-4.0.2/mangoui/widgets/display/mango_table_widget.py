# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 表格控件组件
# @Time   : 2025-11-25 10:30
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoTableWidget(QTableWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QTableWidget {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            outline: none;
            gridline-color: {THEME.bg_300};
            selection-background-color: {THEME.primary_100};
            selection-color: white;
        }}

        QTableWidget::item {{
            padding: 4px;
            border: none;
        }}

        QTableWidget::item:selected {{
            background-color: {THEME.primary_100};
            color: white;
        }}

        QTableWidget::item:hover {{
            background-color: {THEME.bg_200};
        }}

        QHeaderView::section {{
            background-color: {THEME.primary_100};
            color: white;
            padding: 6px;
            border: 1px solid {THEME.primary_200};
            font-weight: bold;
        }}

        QTableWidget:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        """
        self.setStyleSheet(style)