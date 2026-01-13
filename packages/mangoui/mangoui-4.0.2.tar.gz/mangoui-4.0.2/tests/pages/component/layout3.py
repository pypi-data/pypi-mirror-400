# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-02 21:24
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# 从具体的组件模块中导入所需的组件
from mangoui.widgets.container import MangoCard
from mangoui.widgets.display import MangoListWidget
from mangoui.widgets.layout import MangoVBoxLayout, MangoHBoxLayout, MangoGridLayout


class Layout3Page(QWidget):
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
        title = QLabel("基础公共组件展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织基础公共组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        
        # 卡片布局示例
        card_layout_widget = QWidget()
        card_layout = MangoHBoxLayout(card_layout_widget)
        
        for i in range(3):
            card_content_layout = MangoVBoxLayout()
            card_content_layout.addWidget(QLabel(f'卡片 {i+1} 内容'))
            card = MangoCard(card_content_layout, title=f'卡片 {i+1}')
            card_layout.addWidget(card)
        
        self.components_grid.addWidget(QLabel("卡片布局示例:"), 0, 0)
        self.components_grid.addWidget(card_layout_widget, 0, 1)

        # 列表布局示例
        list_widget = MangoListWidget()
        for i in range(10):
            list_widget.addItem(f"列表项 {i+1}")
        
        self.components_grid.addWidget(QLabel("列表布局示例:"), 1, 0)
        self.components_grid.addWidget(list_widget, 1, 1)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)