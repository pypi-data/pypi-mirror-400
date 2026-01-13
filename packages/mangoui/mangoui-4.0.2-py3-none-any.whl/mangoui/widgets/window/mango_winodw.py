# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-17 15:02
# @Author : 毛鹏
from PySide6.QtWidgets import QWidget

from mangoui.widgets.layout.mango_layout import MangoVBoxLayout


class MangoWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = MangoVBoxLayout(self)
