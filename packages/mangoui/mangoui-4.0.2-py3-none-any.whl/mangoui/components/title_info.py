# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-30 14:08
# @Author : 毛鹏

from PySide6.QtWidgets import QWidget

from mangoui.models.models import FieldListModel
from mangoui.widgets.layout import MangoVBoxLayout, MangoGridLayout
from mangoui.widgets.container import MangoCard
from mangoui.widgets.display import MangoLabel


class TitleInfoWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.field_list = None
        self.raw_data = None
        self.layout = MangoVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout = MangoGridLayout()
        self.mango_card = MangoCard(self.grid_layout)
        self.layout.addWidget(self.mango_card)
        self.setLayout(self.layout)

    def init(self, raw_data: dict, field_list: list[FieldListModel]):
        if self.field_list is None and self.raw_data is None:
            self.field_list = field_list
            self.raw_data = raw_data
            row = 0
            column = 0
            for index, item in enumerate(self.field_list):
                if self.raw_data[item.key] and isinstance(self.raw_data[item.key], dict):
                    value = self.raw_data[item.key].get('name')
                else:
                    value = self.raw_data[item.key]
                self.grid_layout.addWidget(MangoLabel(f'{item.name}：{value}'), column, row)
                column += 1
                if index % 3 == 0 and index != 0:
                    row += 1
                    column = 0
