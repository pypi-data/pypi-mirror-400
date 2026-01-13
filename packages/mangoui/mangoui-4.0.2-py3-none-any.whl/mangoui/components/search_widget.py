# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-30 14:08
# @Author : 毛鹏
from PySide6.QtCore import Signal
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME
from mangoui.enums.enums import InputEnum
from mangoui.models.models import SearchDataModel, DialogCallbackModel
from mangoui.widgets.input import (
    MangoLineEdit, MangoComboBox, MangoCascade, MangoToggle, 
    MangoComboBoxMany, MangoPushButton
)


class SearchWidget(QWidget):
    clicked = Signal(object)

    def __init__(self, search_data: list[SearchDataModel]):
        super().__init__()
        self.search_data = search_data
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(self.v_layout)
        for index, search in enumerate(self.search_data):
            if index % 4 == 0 or index == 0:
                but_layout = QHBoxLayout()
                but_layout.setContentsMargins(0, 0, 0, 0)
                self.v_layout.addLayout(but_layout)
            if search.select and callable(search.select):
                select = search.select()
            else:
                select = search.select
            if search.type == InputEnum.INPUT:
                input_object = MangoLineEdit(search.placeholder, '', )
            elif search.type == InputEnum.SELECT:
                input_object = MangoComboBox(search.placeholder, select, search.value, search.subordinate,
                                             key=search.key)
                input_object.setMinimumWidth(145)
            elif search.type == InputEnum.CASCADER:
                input_object = MangoCascade(search.placeholder, select, search.value, search.subordinate,
                                            key=search.key)
                input_object.setMinimumWidth(145)

            elif search.type == InputEnum.TOGGLE:
                input_object = MangoToggle(search.value, key=search.key)
            elif search.type == InputEnum.SELECT_MANY:
                input_object = MangoComboBoxMany(search.placeholder, select)
            else:
                raise ValueError(f'类型错误: {search.type}')
            input_object.click.connect(self.entered)
            from_layout = QFormLayout()
            from_layout.addRow(f'{search.title}：', input_object)
            but_layout.addLayout(from_layout)
            search.input_object = input_object
            if (index + 1) % 4 == 0 or index == len(self.search_data) - 1:
                if (index + 1) % 4 != 0:
                    but_layout.addStretch()

        self.layout.addStretch()
        self.search_but = MangoPushButton('搜索', color=THEME.group.info)
        self.search_but.setMinimumHeight(30)  # 设置最小高度
        self.search_but.setMinimumWidth(50)
        self.search_but.clicked.connect(self.on_search_but_clicked)

        self.layout.addWidget(self.search_but)

        self.reset_but = MangoPushButton('重置', color=THEME.group.error)
        self.reset_but.setMinimumHeight(30)  # 设置最小高度
        self.reset_but.setMinimumWidth(50)
        self.reset_but.clicked.connect(self.on_reset_but_clicked)
        self.layout.addWidget(self.reset_but)

        self.layout.addLayout(self.layout)

    def on_reset_but_clicked(self):
        for search in self.search_data:
            search.input_object.set_value('')
        self.clicked.emit({})

    def entered(self, data: DialogCallbackModel):
        if isinstance(data, DialogCallbackModel):
            for i in self.search_data:
                if i.key == data.subordinate and i.key:
                    data.subordinate_input_object = i.input_object
                    data.key = i.key
                    self.clicked.emit(data)

    def on_search_but_clicked(self):
        data = {}
        for search in self.search_data:
            value = search.input_object.get_value()
            if value:
                data[search.key] = value
        self.clicked.emit(data)
