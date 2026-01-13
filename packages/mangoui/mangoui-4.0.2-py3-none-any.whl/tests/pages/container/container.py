# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-02 21:24
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# 从具体的组件模块中导入所需的组件
from mangoui.widgets.container import (
    MangoCard, MangoGroupBox, MangoStackedWidget, MangoToolBox
)
from mangoui.widgets.input import MangoPushButton
from mangoui.widgets.layout import MangoGridLayout, MangoVBoxLayout, MangoHBoxLayout


class ContainerPage(QWidget):
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
        title = QLabel("容器组件展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织容器组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        self.components_grid.setColumnStretch(3, 1)
        
        # 卡片容器（原有）
        card_layout = MangoVBoxLayout()
        card_layout.addWidget(QLabel('这是卡片内容'))
        self.mango_card = MangoCard(card_layout, title='卡片容器')
        self.components_grid.addWidget(QLabel("卡片容器:"), 0, 0)
        self.components_grid.addWidget(self.mango_card, 0, 1)

        # 分组框组件
        self.mango_group_box = MangoGroupBox("分组框")
        group_layout = MangoVBoxLayout()
        group_layout.addWidget(QLabel("分组框内容"))
        group_layout.addWidget(MangoPushButton("分组框按钮"))
        self.mango_group_box.setLayout(group_layout)
        self.components_grid.addWidget(QLabel("分组框:"), 0, 2)
        self.components_grid.addWidget(self.mango_group_box, 0, 3)

        # 堆叠窗口组件
        self.mango_stacked_widget = MangoStackedWidget()
        page1 = QLabel("堆叠页面1")
        page2 = QLabel("堆叠页面2")
        page3 = QLabel("堆叠页面3")
        self.mango_stacked_widget.addWidget(page1)
        self.mango_stacked_widget.addWidget(page2)
        self.mango_stacked_widget.addWidget(page3)
        self.components_grid.addWidget(QLabel("堆叠窗口:"), 1, 0)
        self.components_grid.addWidget(self.mango_stacked_widget, 1, 1)

        # 添加切换按钮
        switch_layout = MangoHBoxLayout()
        switch_btn1 = MangoPushButton("页面1")
        switch_btn2 = MangoPushButton("页面2")
        switch_btn3 = MangoPushButton("页面3")
        switch_btn1.clicked.connect(lambda: self.mango_stacked_widget.setCurrentIndex(0))
        switch_btn2.clicked.connect(lambda: self.mango_stacked_widget.setCurrentIndex(1))
        switch_btn3.clicked.connect(lambda: self.mango_stacked_widget.setCurrentIndex(2))
        switch_layout.addWidget(switch_btn1)
        switch_layout.addWidget(switch_btn2)
        switch_layout.addWidget(switch_btn3)
        
        switch_widget = QWidget()
        switch_widget.setLayout(switch_layout)
        self.components_grid.addWidget(switch_widget, 2, 0, 1, 2)

        # 工具箱组件
        self.mango_tool_box = MangoToolBox()
        toolbox_page1 = QLabel("工具箱页面1")
        toolbox_page2 = QLabel("工具箱页面2")
        toolbox_page3 = QLabel("工具箱页面3")
        self.mango_tool_box.addItem(toolbox_page1, "工具1")
        self.mango_tool_box.addItem(toolbox_page2, "工具2")
        self.mango_tool_box.addItem(toolbox_page3, "工具3")
        self.components_grid.addWidget(QLabel("工具箱:"), 1, 2)
        self.components_grid.addWidget(self.mango_tool_box, 1, 3, 2, 2)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)