# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-02 21:24
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# 从具体的组件模块中导入所需的组件
from mangoui.widgets.input import (
    MangoLineEdit, MangoSpinBox, MangoComboBox, MangoPushButton
)
from mangoui.models.models import ComboBoxDataModel
from mangoui.widgets.layout import MangoVBoxLayout, MangoGridLayout, MangoFormLayout


class Layout2Page(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = MangoVBoxLayout(self)
        
        # 创建滚动区域以容纳所有组件
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = MangoVBoxLayout(self.scroll_widget)
        
        # 标题
        title = QLabel("高级布局展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织高级布局组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        
        # 表单布局示例
        form_widget = QWidget()
        form_layout = MangoFormLayout(form_widget)
        form_layout.addRow(QLabel("姓名:"), MangoLineEdit("请输入姓名"))
        form_layout.addRow(QLabel("邮箱:"), MangoLineEdit("请输入邮箱"))
        form_layout.addRow(QLabel("年龄:"), MangoSpinBox())
        # 创建具有 name 和 id 属性的对象
        gender_data = [
            type('obj', (object,), {'id': 1, 'name': '男'})(),
            type('obj', (object,), {'id': 2, 'name': '女'})()
        ]
        form_layout.addRow(QLabel("性别:"), MangoComboBox("请选择性别", gender_data))
        
        self.components_grid.addWidget(QLabel("表单布局示例:"), 0, 0)
        self.components_grid.addWidget(form_widget, 0, 1)

        # 分割布局示例
        splitter = QSplitter(Qt.Horizontal)  # type: ignore
        left_panel = QTextEdit("左侧面板")
        center_panel = QTextEdit("中间面板")
        right_panel = QTextEdit("右侧面板")
        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)
        
        self.components_grid.addWidget(QLabel("分割布局示例:"), 1, 0)
        self.components_grid.addWidget(splitter, 1, 1)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)