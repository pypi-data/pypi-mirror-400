# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 列表视图组件
# @Time   : 2025-11-25 10:20
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoListView(QListView):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QListView {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            outline: none;
            padding: 2px;
        }}

        QListView::item {{
            padding: 8px 12px;
            border-radius: {THEME.border_radius};
        }}

        QListView::item:selected {{
            background-color: {THEME.primary_100};
            color: white;
        }}

        QListView::item:hover {{
            background-color: {THEME.bg_200};
        }}

        QListView::item:selected:hover {{
            background-color: {THEME.primary_200};
        }}

        QListView:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        
        QListView QScrollBar:vertical {{
            border: none;
            background: {THEME.bg_300};
            width: 8px;
            margin: 0px 0px 0px 0px;
            border-radius: 0px;
        }}
        
        QListView QScrollBar::handle:vertical {{
            background: {THEME.bg_300};
            min-height: 25px;
            border-radius: 4px;
        }}
        """
        self.setStyleSheet(style)


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

        QListWidget::item:selected:hover {{
            background-color: {THEME.primary_200};
        }}

        QListWidget:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        
        QListWidget QScrollBar:vertical {{
            border: none;
            background: {THEME.bg_300};
            width: 8px;
            margin: 0px 0px 0px 0px;
            border-radius: 0px;
        }}
        
        QListWidget QScrollBar::handle:vertical {{
            background: {THEME.bg_300};
            min-height: 25px;
            border-radius: 4px;
        }}
        """
        self.setStyleSheet(style)