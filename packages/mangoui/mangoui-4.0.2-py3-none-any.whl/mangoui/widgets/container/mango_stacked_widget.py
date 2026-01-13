# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 堆叠窗口组件
# @Time   : 2025-11-25 10:50
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoStackedWidget(QStackedWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QStackedWidget {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
        }}

        QStackedWidget:disabled {{
            background-color: {THEME.bg_200};
        }}
        """
        self.setStyleSheet(style)