# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-02 21:24
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# 从具体的组件模块中导入所需的组件
from mangoui.widgets.display import (
    MangoTreeWidget, MangoTableWidget
)
from mangoui.widgets.layout import MangoVBoxLayout, MangoGridLayout


class Layout4Page(QWidget):
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
        title = QLabel("高级公共组件展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织高级公共组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        
        # 树形布局示例
        tree_widget = MangoTreeWidget()
        root = QTreeWidgetItem(tree_widget, ["根节点"])
        for i in range(3):
            child = QTreeWidgetItem(root, [f"子节点 {i+1}"])
            for j in range(2):
                QTreeWidgetItem(child, [f"子节点 {i+1}-{j+1}"])
        tree_widget.expandAll()
        
        self.components_grid.addWidget(QLabel("树形布局示例:"), 0, 0)
        self.components_grid.addWidget(tree_widget, 0, 1)

        # 表格布局示例
        table_widget = MangoTableWidget()
        table_widget.setRowCount(5)
        table_widget.setColumnCount(3)
        table_widget.setHorizontalHeaderLabels(["列1", "列2", "列3"])
        for i in range(5):
            for j in range(3):
                table_widget.setItem(i, j, QTableWidgetItem(f"数据 {i+1}-{j+1}"))
        
        self.components_grid.addWidget(QLabel("表格布局示例:"), 1, 0)
        self.components_grid.addWidget(table_widget, 1, 1)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)