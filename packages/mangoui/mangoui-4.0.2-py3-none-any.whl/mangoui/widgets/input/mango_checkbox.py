# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-08-24 17:16
# @Author : 毛鹏

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class MangoCheckBox(QCheckBox):
    def __init__(self, text=None, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.get_style()

    def get_style(self):
        from mangoui.settings.settings import THEME
        style = f"""
        QCheckBox {{
            spacing: 8px;
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 4px;
            border: 1px solid {THEME.bg_300};
            background-color: {THEME.bg_100};
        }}
        
        QCheckBox::indicator:hover {{
            border: 1px solid {THEME.primary_100};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {THEME.primary_100};
            border: 1px solid {THEME.primary_100};
            image: url(:/icons/check.svg);
        }}
        
        QCheckBox:disabled {{
            color: {THEME.text_200};
        }}
        
        QCheckBox::indicator:disabled {{
            background-color: {THEME.bg_200};
            border: 1px solid {THEME.bg_300};
        }}
        
        QCheckBox::indicator:checked:disabled {{
            background-color: {THEME.bg_300};
            border: 1px solid {THEME.bg_300};
            image: url(:/icons/check_disabled.svg);
        }}
        """
        self.setStyleSheet(style)

    def isChecked(self):
        return super().isChecked()

    def setChecked(self, checked):
        super().setChecked(checked)