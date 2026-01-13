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


class LayoutPage(QWidget):
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
        title = QLabel("布局组件展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织布局组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        self.components_grid.setColumnStretch(3, 1)
        
        # 三栏布局示例
        layout_widget = QWidget()
        main_layout = MangoHBoxLayout(layout_widget)
        
        # 左侧布局
        left_widget = QWidget()
        left_layout = MangoVBoxLayout(left_widget)
        left_layout.addWidget(QLabel("左侧内容1"))
        left_layout.addWidget(MangoPushButton("左侧按钮"))
        left_layout.addWidget(QLabel("左侧内容2"))
        
        # 中间布局
        center_widget = QWidget()
        center_layout = MangoVBoxLayout(center_widget)
        center_layout.addWidget(QLabel("中间内容1"))
        center_layout.addWidget(MangoPushButton("中间按钮"))
        center_layout.addWidget(QLabel("中间内容2"))
        
        # 右侧布局
        right_widget = QWidget()
        right_layout = MangoVBoxLayout(right_widget)
        right_layout.addWidget(QLabel("右侧内容1"))
        right_layout.addWidget(MangoPushButton("右侧按钮"))
        right_layout.addWidget(QLabel("右侧内容2"))
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(center_widget)
        main_layout.addWidget(right_widget)
        
        self.components_grid.addWidget(QLabel("三栏布局示例:"), 0, 0)
        self.components_grid.addWidget(layout_widget, 0, 1, 1, 3)

        # 网格布局示例
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        for i in range(3):
            for j in range(3):
                grid_layout.addWidget(MangoPushButton(f"按钮{i+1}-{j+1}"), i, j)
        
        self.components_grid.addWidget(QLabel("网格布局示例:"), 1, 0)
        self.components_grid.addWidget(grid_widget, 1, 1, 1, 3)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)