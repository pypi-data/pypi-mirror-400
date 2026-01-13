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
from mangoui.components import (
    success_message, error_message, warning_message, info_message, error_notification,success_notification, warning_notification,info_notification
)
from mangoui.widgets.layout import MangoVBoxLayout, MangoGridLayout


class FeedbackPage(QWidget):
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
        title = QLabel("反馈组件展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织反馈组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        
        # 成功消息按钮
        success_btn = MangoPushButton('成功消息')
        success_btn.clicked.connect(self.success_message)
        self.components_grid.addWidget(QLabel("成功消息:"), 0, 0)
        self.components_grid.addWidget(success_btn, 0, 1)

        # 错误消息按钮
        error_btn = MangoPushButton('错误消息')
        error_btn.clicked.connect(self.error_message)
        self.components_grid.addWidget(QLabel("错误消息:"), 1, 0)
        self.components_grid.addWidget(error_btn, 1, 1)

        # 警告消息按钮
        warning_btn = MangoPushButton('警告消息')
        warning_btn.clicked.connect(self.warning_message)
        self.components_grid.addWidget(QLabel("警告消息:"), 2, 0)
        self.components_grid.addWidget(warning_btn, 2, 1)

        # 信息消息按钮
        info_btn = MangoPushButton('信息消息')
        info_btn.clicked.connect(self.info_message)
        self.components_grid.addWidget(QLabel("信息消息:"), 3, 0)
        self.components_grid.addWidget(info_btn, 3, 1)
        
        # 成功通知按钮
        success_notification_btn = MangoPushButton('成功通知')
        success_notification_btn.clicked.connect(self.success_notification)
        self.components_grid.addWidget(QLabel("成功通知:"), 4, 0)
        self.components_grid.addWidget(success_notification_btn, 4, 1)

        # 错误通知按钮
        error_notification_btn = MangoPushButton('错误通知')
        error_notification_btn.clicked.connect(self.error_notification)
        self.components_grid.addWidget(QLabel("错误通知:"), 5, 0)
        self.components_grid.addWidget(error_notification_btn, 5, 1)

        # 警告通知按钮
        warning_notification_btn = MangoPushButton('警告通知')
        warning_notification_btn.clicked.connect(self.warning_notification)
        self.components_grid.addWidget(QLabel("警告通知:"), 6, 0)
        self.components_grid.addWidget(warning_notification_btn, 6, 1)

        # 信息通知按钮
        info_notification_btn = MangoPushButton('信息通知')
        info_notification_btn.clicked.connect(self.info_notification)
        self.components_grid.addWidget(QLabel("信息通知:"), 7, 0)
        self.components_grid.addWidget(info_notification_btn, 7, 1)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)

    def success_message(self, _):
        success_message(self, '这是一个成功的提示')

    def error_message(self, _):
        error_message(self, '这是一个错误的提示')

    def warning_message(self, _):
        warning_message(self, '这是一个警告的提示')

    def info_message(self, _):
        info_message(self, '这是一个信息的提示')
        
    def success_notification(self, _):
        success_notification(self, '这是一个成功的通知')

    def error_notification(self, _):
        error_notification(self, '这是一个错误的通知')

    def warning_notification(self, _):
        warning_notification(self, '这是一个警告的通知')

    def info_notification(self, _):
        info_notification(self, '这是一个信息的通知')