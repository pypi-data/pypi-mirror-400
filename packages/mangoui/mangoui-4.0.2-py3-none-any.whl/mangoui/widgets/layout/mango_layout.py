# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-17 14:55
# @Author : 毛鹏
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout


class MangoVBoxLayout(QVBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignTop)  # type: ignore


class MangoHBoxLayout(QHBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignLeft)  # type: ignore


class MangoFormLayout(QFormLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignLeft)  # type: ignore


class MangoGridLayout(QGridLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignLeft)  # type: ignore