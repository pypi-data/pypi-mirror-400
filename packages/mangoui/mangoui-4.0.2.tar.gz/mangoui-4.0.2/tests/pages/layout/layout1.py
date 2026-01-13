# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-02 21:24
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# 从具体的组件模块中导入所需的组件
from mangoui.widgets.input import MangoPushButton
from mangoui.widgets.layout import MangoVBoxLayout, MangoHBoxLayout, MangoGridLayout


class Layout1Page(QWidget):
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
        title = QLabel("基础布局展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织基础布局组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        
        # 垂直布局示例
        vbox_widget = QWidget()
        vbox_layout = MangoVBoxLayout(vbox_widget)
        vbox_layout.addWidget(QLabel("垂直布局 - 项目1"))
        vbox_layout.addWidget(MangoPushButton("垂直布局 - 按钮1"))
        vbox_layout.addWidget(QLabel("垂直布局 - 项目2"))
        vbox_layout.addWidget(MangoPushButton("垂直布局 - 按钮2"))
        
        self.components_grid.addWidget(QLabel("垂直布局示例:"), 0, 0)
        self.components_grid.addWidget(vbox_widget, 0, 1)

        # 水平布局示例
        hbox_widget = QWidget()
        hbox_layout = MangoHBoxLayout(hbox_widget)
        hbox_layout.addWidget(QLabel("水平布局 - 项目1"))
        hbox_layout.addWidget(MangoPushButton("水平布局 - 按钮1"))
        hbox_layout.addWidget(QLabel("水平布局 - 项目2"))
        hbox_layout.addWidget(MangoPushButton("水平布局 - 按钮2"))
        
        self.components_grid.addWidget(QLabel("水平布局示例:"), 1, 0)
        self.components_grid.addWidget(hbox_widget, 1, 1)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)