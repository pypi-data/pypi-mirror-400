# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: LCD数字显示组件
# @Time   : 2025-11-25 11:15
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoLCDNumber(QLCDNumber):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.setSegmentStyle(QLCDNumber.Filled)  # type: ignore
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QLCDNumber {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            color: {THEME.primary_100};
        }}

        QLCDNumber:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        """
        self.setStyleSheet(style)