# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 纯文本编辑器组件
# @Time   : 2025-11-25 10:15
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoPlainTextEdit(QPlainTextEdit):
    click = Signal(object)

    def __init__(self, placeholder="", value: str | None = None, subordinate: str | None = None, parent=None, **kwargs):
        super().__init__(parent)
        self.placeholder = placeholder
        self.value = value
        self.subordinate = subordinate
        self.kwargs = kwargs
        
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
        QPlainTextEdit {{
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

        QPlainTextEdit:focus {{
            border: 1px solid {THEME.primary_100};
            background-color: {THEME.bg_100};
        }}
        
        QPlainTextEdit:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        
        QPlainTextEdit QScrollBar:vertical {{
            border: none;
            background: {THEME.bg_300};
            width: 8px;
            margin: 0px 0px 0px 0px;
            border-radius: 0px;
        }}
        
        QPlainTextEdit QScrollBar::handle:vertical {{
            background: {THEME.bg_300};
            min-height: 25px;
            border-radius: 4px;
        }}
        """
        self.setStyleSheet(style)