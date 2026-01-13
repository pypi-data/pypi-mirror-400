# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-08-28 16:33
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# 从具体的组件模块中导入所需的组件
from mangoui.widgets.window import MangoScrollArea
from mangoui.widgets.container import MangoCard
from mangoui.widgets.layout import MangoVBoxLayout, MangoGridLayout


class ComponentPage(QWidget):
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
        title = QLabel("公共组件展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织公共组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        
        # 页面标题和描述
        self.title_label = QLabel(self.scroll_widget)
        self.title_label.setText("页面组件")
        self.title_label.setMaximumSize(QSize(16777215, 40))
        font = QFont()
        font.setPointSize(16)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet("font-size: 16pt")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.components_grid.addWidget(self.title_label, 0, 0, 1, 2)
        
        self.description_label = QLabel(self.scroll_widget)
        self.description_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.description_label.setText("以下是所有自定义小部件\n哈哈哈哈哈")
        self.description_label.setWordWrap(True)
        self.components_grid.addWidget(self.description_label, 1, 0, 1, 2)

        # 滚动区域组件
        self.scroll_area_content = MangoScrollArea()
        content_widget = QWidget()
        content_layout = MangoVBoxLayout(content_widget)
        content_layout.addWidget(QLabel("滚动区域内容1"))
        content_layout.addWidget(QLabel("滚动区域内容2"))
        content_layout.addWidget(QLabel("滚动区域内容3"))
        content_layout.addWidget(QLabel("滚动区域内容4"))
        content_layout.addWidget(QLabel("滚动区域内容5"))
        self.scroll_area_content.setWidget(content_widget)
        self.components_grid.addWidget(QLabel("滚动区域:"), 2, 0)
        self.components_grid.addWidget(self.scroll_area_content, 2, 1)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)

    def load_data(self):
        # 模拟延迟加载数据
        QTimer.singleShot(3000, self.show_data)  # 3秒后调用show_data方法

    def show_data(self):
        pass
    def load_data(self):
        # 模拟延迟加载数据
        QTimer.singleShot(3000, self.show_data)  # 3秒后调用show_data方法

    def show_data(self):
        pass