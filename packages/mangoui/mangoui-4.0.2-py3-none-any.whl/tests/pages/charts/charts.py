# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-02 21:24
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# 从具体的组件模块中导入所需的组件
from mangoui.widgets.charts import (
    MangoLinePlot, MangoPiePlot
)
from mangoui.widgets.layout import MangoVBoxLayout, MangoGridLayout


class ChartsPage(QWidget):
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
        title = QLabel("图表组件展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织图表组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        
        # 折线图
        self.line_chart = MangoLinePlot("折线图标题", "Y轴标签", "X轴标签")
        self.components_grid.addWidget(QLabel("折线图:"), 0, 0)
        self.components_grid.addWidget(self.line_chart, 0, 1)

        # 饼图
        self.pie_chart = MangoPiePlot()
        self.components_grid.addWidget(QLabel("饼图:"), 1, 0)
        self.components_grid.addWidget(self.pie_chart, 1, 1)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)