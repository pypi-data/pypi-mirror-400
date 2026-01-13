# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-08-30 14:52
# @Author : 毛鹏
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFormLayout, QSpacerItem, QSizePolicy, QHBoxLayout

from mangoui.settings.settings import THEME
from mangoui.enums.enums import *
from mangoui.models.models import FormDataModel, DialogCallbackModel
from mangoui.widgets.window import MangoDialog
from mangoui.widgets.input import (
    MangoLineEdit, MangoComboBox, MangoCascade, MangoToggle, 
    MangoComboBoxMany, MangoTextEdit, MangoPushButton
)


class DialogWidget(MangoDialog):
    clicked = Signal(object)

    def __init__(self, tips: str, form_data: list[FormDataModel], size: tuple = (400, 300)):
        super().__init__(tips, size)
        self.form_data = form_data
        form_layout = QFormLayout()
        for form in self.form_data:
            if form.type == InputEnum.INPUT:
                input_object = MangoLineEdit(form.placeholder, form.value, form.subordinate, key=form.key)
            elif form.type == InputEnum.SELECT:
                input_object = MangoComboBox(form.placeholder, form.select, form.value, form.subordinate, key=form.key)
            elif form.type == InputEnum.CASCADER:
                input_object = MangoCascade(form.placeholder, form.select, form.value, form.subordinate, key=form.key)
            elif form.type == InputEnum.TOGGLE:
                input_object = MangoToggle(form.value, key=form.key)
            elif form.type == InputEnum.SELECT_MANY:
                input_object = MangoComboBoxMany(form.placeholder, form.select, form.value)
            elif form.type == InputEnum.TEXT:
                input_object = MangoTextEdit(form.placeholder, form.value, form.subordinate)
            else:
                raise ValueError(f'类型错误: {form.type}')
            input_object.click.connect(self.entered)
            if form.required:
                form_layout.addRow(f"*{form.title}:", input_object)
            else:
                form_layout.addRow(f"{form.title}:", input_object)

            form.input_object = input_object

        self.layout.addLayout(form_layout)
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        button_layout = QHBoxLayout()
        self.layout.addLayout(button_layout)
        button_layout.addStretch()
        cancel_button = MangoPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        submit_button = MangoPushButton("提交", color=THEME.group.info)
        submit_button.clicked.connect(self.submit_form)
        button_layout.addWidget(submit_button)

        self.data = {}

    def submit_form(self):
        for form in self.form_data:
            value = form.input_object.get_value()
            if form.required:
                if value is None or value == '':
                    from mangoui.components import error_message
                    self.data = {}
                    error_message(self, f'{form.title} 是必填项')
                    return
            if value == '':
                self.data[form.key] = None
            else:
                self.data[form.key] = value
        self.accept()  # 关闭对话框

    def entered(self, data: DialogCallbackModel):
        if isinstance(data, DialogCallbackModel):
            for i in self.form_data:
                if i.key == data.subordinate and i.key:
                    data.subordinate_input_object = i.input_object
                    data.key = i.key
                    self.clicked.emit(data)

    def check_value(self, value):
        pass
