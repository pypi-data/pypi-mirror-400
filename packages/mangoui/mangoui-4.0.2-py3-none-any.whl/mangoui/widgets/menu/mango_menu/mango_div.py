# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏

from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoDiv(QWidget):
    def __init__(self, color=None):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 0, 5, 0)

        self.frame_line = QFrame()
        if color:
            self.frame_line.setStyleSheet(f"background: {color};")
        else:
            self.frame_line.setStyleSheet(f"background: {THEME.bg_300};")

        self.frame_line.setMaximumHeight(1)
        self.frame_line.setMinimumHeight(1)
        self.layout.addWidget(self.frame_line)
        self.setMaximumHeight(0)