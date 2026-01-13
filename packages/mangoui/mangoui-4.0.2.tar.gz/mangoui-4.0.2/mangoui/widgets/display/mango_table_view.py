# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 表格视图组件
# @Time   : 2025-11-25 10:30
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoTableView(QTableView):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QTableView {{
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

        QTableView::item {{
            padding: 8px 12px;
        }}

        QTableView::item:selected {{
            background-color: {THEME.primary_100};
            color: white;
        }}

        QTableView::item:hover {{
            background-color: {THEME.bg_200};
        }}

        QTableView::item:selected:hover {{
            background-color: {THEME.primary_200};
        }}

        QHeaderView::section {{
            background-color: {THEME.primary_100};
            color: white;
            padding: 8px 12px;
            border: 1px solid {THEME.primary_200};
            font-weight: bold;
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}

        QHeaderView::section:hover {{
            background-color: {THEME.primary_200};
        }}

        QTableView QTableCornerButton::section {{
            background-color: {THEME.primary_100};
            border: 1px solid {THEME.primary_200};
        }}

        QTableView:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        
        QTableView QScrollBar:vertical {{
            border: none;
            background: {THEME.bg_300};
            width: 8px;
            margin: 0px 0px 0px 0px;
            border-radius: 0px;
        }}
        
        QTableView QScrollBar::handle:vertical {{
            background: {THEME.bg_300};
            min-height: 25px;
            border-radius: 4px;
        }}
        
        QTableView QScrollBar:horizontal {{
            border: none;
            background: {THEME.bg_300};
            height: 8px;
            margin: 0px 0px 0px 0px;
            border-radius: 0px;
        }}
        
        QTableView QScrollBar::handle:horizontal {{
            background: {THEME.bg_300};
            min-width: 25px;
            border-radius: 4px;
        }}
        """
        self.setStyleSheet(style)


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
            padding: 8px 12px;
        }}

        QTableWidget::item:selected {{
            background-color: {THEME.primary_100};
            color: white;
        }}

        QTableWidget::item:hover {{
            background-color: {THEME.bg_200};
        }}

        QTableWidget::item:selected:hover {{
            background-color: {THEME.primary_200};
        }}

        QHeaderView::section {{
            background-color: {THEME.primary_100};
            color: white;
            padding: 8px 12px;
            border: 1px solid {THEME.primary_200};
            font-weight: bold;
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}

        QHeaderView::section:hover {{
            background-color: {THEME.primary_200};
        }}

        QTableWidget QTableCornerButton::section {{
            background-color: {THEME.primary_100};
            border: 1px solid {THEME.primary_200};
        }}

        QTableWidget:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        
        QTableWidget QScrollBar:vertical {{
            border: none;
            background: {THEME.bg_300};
            width: 8px;
            margin: 0px 0px 0px 0px;
            border-radius: 0px;
        }}
        
        QTableWidget QScrollBar::handle:vertical {{
            background: {THEME.bg_300};
            min-height: 25px;
            border-radius: 4px;
        }}
        
        QTableWidget QScrollBar:horizontal {{
            border: none;
            background: {THEME.bg_300};
            height: 8px;
            margin: 0px 0px 0px 0px;
            border-radius: 0px;
        }}
        
        QTableWidget QScrollBar::handle:horizontal {{
            background: {THEME.bg_300};
            min-width: 25px;
            border-radius: 4px;
        }}
        """
        self.setStyleSheet(style)