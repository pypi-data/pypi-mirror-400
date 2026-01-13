# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 字体下拉框组件
# @Time   : 2025-11-25 10:40
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoFontComboBox(QFontComboBox):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QFontComboBox {{
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

        QFontComboBox:focus {{
            border: 1px solid {THEME.primary_100};
            background-color: {THEME.bg_100};
        }}
        
        QFontComboBox:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        
        QFontComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: {THEME.bg_300};
            border-left-style: solid;
            border-top-right-radius: {THEME.border_radius};
            border-bottom-right-radius: {THEME.border_radius};
        }}

        QFontComboBox::down-arrow {{
            image: url(:/icons/down.svg);
            width: 12px;
            height: 12px;
        }}
        
        QFontComboBox QAbstractItemView {{
            background-color: {THEME.bg_100};
            border: 1px solid {THEME.bg_300};
            border-radius: {THEME.border_radius};
            selection-background-color: {THEME.primary_100};
            selection-color: white;
        }}
        """
        self.setStyleSheet(style)
        self.setMinimumHeight(36)