# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-30 14:08
# @Author : 毛鹏
from functools import partial

from PySide6.QtCore import Signal
from PySide6.QtWidgets import *

from mangoui.models.models import RightDataModel
from mangoui.widgets.input import MangoPushButton


class RightButton(QWidget):
    clicked = Signal(object)

    def __init__(self, but_list_obj: list[RightDataModel]):
        super().__init__()
        self.but_list_obj = but_list_obj
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addStretch()
        for but_obj in self.but_list_obj:
            but_obj.obj = MangoPushButton(but_obj.name, color=but_obj.theme)
            but_obj.obj.clicked.connect(partial(self.but_clicked, but_obj.action))
            self.layout.addWidget(but_obj.obj)
        self.setLayout(self.layout)

    def but_clicked(self, action):
        self.clicked.emit({'action': action, 'row': None})
