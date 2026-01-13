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
from mangoui.widgets.display import MangoLabel
from mangoui.widgets.layout import MangoVBoxLayout, MangoHBoxLayout, MangoGridLayout
from mangoui.widgets.window import MangoScrollArea


class HomePage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = MangoVBoxLayout(self)
        
        # 创建滚动区域以容纳所有组件
        self.scroll_area = MangoScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = MangoVBoxLayout(self.scroll_widget)
        self.scroll_layout.setAlignment(Qt.AlignTop)  # type: ignore
        
        # 标题
        title = QLabel("芒果PySide6组件库")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px 0; color: #8a7aa0;")
        title.setAlignment(Qt.AlignCenter)  # type: ignore
        self.scroll_layout.addWidget(title)

        # 描述
        description = QLabel("欢迎使用芒果PySide6组件库！\n\n"
                           "这是一个基于PySide6的现代化UI组件库，提供了丰富的组件和布局方案。\n"
                           "通过左侧导航菜单可以查看各种组件的示例和用法。")
        description.setStyleSheet("font-size: 14px; margin: 20px; text-align: center;")
        description.setAlignment(Qt.AlignCenter)  # type: ignore
        description.setWordWrap(True)
        self.scroll_layout.addWidget(description)

        # 使用网格布局组织主页组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setAlignment(Qt.AlignTop)  # type: ignore
        self.components_grid.setSpacing(20)
        
        # 组件统计
        stats_layout = MangoHBoxLayout()
        stats_layout.setSpacing(20)
        
        # 为每个卡片创建布局
        stats_layout1 = MangoVBoxLayout()
        stats_label1 = QLabel("15+ 组件")
        stats_label1.setStyleSheet("font-size: 16px; font-weight: bold; color: #8a7aa0;")
        stats_label1.setAlignment(Qt.AlignCenter)  # type: ignore
        stats_layout1.addWidget(stats_label1)
        stats_card1 = MangoCard(stats_layout1, title="输入组件")
        stats_card1.setFixedHeight(120)
        
        stats_layout2 = MangoVBoxLayout()
        stats_label2 = QLabel("12+ 组件")
        stats_label2.setStyleSheet("font-size: 16px; font-weight: bold; color: #8a7aa0;")
        stats_label2.setAlignment(Qt.AlignCenter)  # type: ignore
        stats_layout2.addWidget(stats_label2)
        stats_card2 = MangoCard(stats_layout2, title="显示组件")
        stats_card2.setFixedHeight(120)
        
        stats_layout3 = MangoVBoxLayout()
        stats_label3 = QLabel("5+ 组件")
        stats_label3.setStyleSheet("font-size: 16px; font-weight: bold; color: #8a7aa0;")
        stats_label3.setAlignment(Qt.AlignCenter)  # type: ignore
        stats_layout3.addWidget(stats_label3)
        stats_card3 = MangoCard(stats_layout3, title="容器组件")
        stats_card3.setFixedHeight(120)
        
        stats_layout4 = MangoVBoxLayout()
        stats_label4 = QLabel("3+ 组件")
        stats_label4.setStyleSheet("font-size: 16px; font-weight: bold; color: #8a7aa0;")
        stats_label4.setAlignment(Qt.AlignCenter)  # type: ignore
        stats_layout4.addWidget(stats_label4)
        stats_card4 = MangoCard(stats_layout4, title="菜单组件")
        stats_card4.setFixedHeight(120)
        
        stats_layout.addWidget(stats_card1)
        stats_layout.addWidget(stats_card2)
        stats_layout.addWidget(stats_card3)
        stats_layout.addWidget(stats_card4)
        
        stats_widget = QWidget()
        stats_widget.setLayout(stats_layout)
        self.components_grid.addWidget(stats_widget, 0, 0, 1, 2)

        # 特性介绍
        features_label = QLabel("特性介绍:")
        features_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px 0 10px 0; color: #383738;")
        
        features_widget = QWidget()
        features_layout = MangoVBoxLayout(features_widget)
        features_layout.setSpacing(10)
        features = [
            "现代化UI设计，支持主题定制",
            "丰富的组件库，涵盖常用UI元素",
            "响应式布局，适配不同屏幕尺寸",
            "易于扩展和自定义",
            "完善的文档和示例"
        ]
        
        for feature in features:
            feature_label = QLabel(f"• {feature}")
            feature_label.setStyleSheet("font-size: 14px; margin: 5px 20px; color: #383738;")
            feature_label.setWordWrap(True)
            features_layout.addWidget(feature_label)
        
        # 创建特性卡片
        features_card = MangoCard(features_layout)
        features_card.setFixedHeight(200)
        
        self.components_grid.addWidget(features_label, 1, 0)
        self.components_grid.addWidget(features_card, 2, 0, 1, 2)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 添加一些间距
        self.scroll_layout.addStretch()

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)