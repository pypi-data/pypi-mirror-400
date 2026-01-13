# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-02 21:24
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# 从具体的组件模块中导入所需的组件
from mangoui.widgets.window import (
    MangoDialog, MangoFrame, MangoTree
)
from mangoui.widgets.input import MangoPushButton
from mangoui.widgets.layout import MangoVBoxLayout, MangoGridLayout


class WindowPage(QWidget):
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
        title = QLabel("窗口组件展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织窗口组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        
        # 对话框组件
        dialog_btn = MangoPushButton("打开对话框")
        dialog_btn.clicked.connect(self.show_dialog)
        self.components_grid.addWidget(QLabel("对话框:"), 0, 0)
        self.components_grid.addWidget(dialog_btn, 0, 1)

        # 框架组件
        self.mango_frame = MangoFrame(self)
        frame_layout = MangoVBoxLayout(self.mango_frame)
        frame_layout.addWidget(QLabel("框架内容"))
        self.components_grid.addWidget(QLabel("框架:"), 1, 0)
        self.components_grid.addWidget(self.mango_frame, 1, 1)

        # 树组件
        self.mango_tree = MangoTree("树组件标题")
        tree_layout = MangoVBoxLayout(self.mango_tree)
        tree_layout.addWidget(QLabel("树组件内容"))
        self.components_grid.addWidget(QLabel("树组件:"), 2, 0)
        self.components_grid.addWidget(self.mango_tree, 2, 1)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)

    def show_dialog(self):
        dialog = MangoDialog(self)
        dialog.setWindowTitle("测试对话框")
        layout = MangoVBoxLayout(dialog)
        layout.addWidget(QLabel("这是一个测试对话框"))
        ok_btn = MangoPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        layout.addWidget(ok_btn)
        dialog.exec()