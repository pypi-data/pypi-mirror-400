# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-18 11:11
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoTextEdit(QTextEdit):
    click = Signal(object)

    def __init__(self, placeholder, value: str | None = None, subordinate: str | None = None):
        super().__init__()
        self.value = value
        self.subordinate = subordinate

        if placeholder:
            self.setPlaceholderText(placeholder)

        if self.value:
            self.set_value(self.value)
        self.set_stylesheet()

    def set_value(self, text: str):
        self.setPlainText(text)

    def get_value(self):
        return self.toPlainText()

    def set_stylesheet(self):
        style = f"""
        QTextEdit {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            padding: 8px 12px;
            selection-color: white;
            selection-background-color: {THEME.primary_100};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            outline: none;
        }}

        QTextEdit:focus {{
            border: 1px solid {THEME.primary_100};
            background-color: {THEME.bg_100};
        }}
        
        QTextEdit:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        
        /* 添加滚动条样式以匹配全局样式 */
        QTextEdit QScrollBar:horizontal {{
            border: none;
            background: {THEME.bg_300};
            height: 8px;
            margin: 0px 21px;
            border-radius: 0px;
        }}
        
        QTextEdit QScrollBar::handle:horizontal {{
            background: {THEME.bg_300};
            min-width: 25px;
            border-radius: 4px;
        }}
        
        QTextEdit QScrollBar::add-line:horizontal {{
            border: none;
            background: {THEME.bg_300};
            width: 20px;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }}
        
        QTextEdit QScrollBar::sub-line:horizontal {{
            border: none;
            background: {THEME.bg_300};
            width: 20px;
            border-top-left-radius: 4px;
            border-bottom-left-radius: 4px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }}
        
        QTextEdit QScrollBar::up-arrow:horizontal, QTextEdit QScrollBar::down-arrow:horizontal {{
            background: none;
        }}
        
        QTextEdit QScrollBar::add-page:horizontal, QTextEdit QScrollBar::sub-page:horizontal {{
            background: none;
        }}
        
        QTextEdit QScrollBar:vertical {{
            border: none;
            background: {THEME.bg_300};
            width: 8px;
            margin: 21px 0;
            border-radius: 0px;
        }}
        
        QTextEdit QScrollBar::handle:vertical {{
            background: {THEME.bg_300};
            min-height: 25px;
            border-radius: 4px;
        }}
        
        QTextEdit QScrollBar::add-line:vertical {{
            border: none;
            background: {THEME.bg_300};
            height: 20px;
            border-bottom-left-radius: 4px;
            border-bottom-right-radius: 4px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }}
        
        QTextEdit QScrollBar::sub-line:vertical {{
            border: none;
            background: {THEME.bg_300};
            height: 20px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }}
        
        QTextEdit QScrollBar::up-arrow:vertical, QTextEdit QScrollBar::down-arrow:vertical {{
            background: none;
        }}
        
        QTextEdit QScrollBar::add-page:vertical, QTextEdit QScrollBar::sub-page:vertical {{
            background: none;
        }}
        """
        self.setStyleSheet(style)
