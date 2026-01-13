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
    MangoProgressBar, MangoCircularProgress, MangoLabel, MangoMessage,
    MangoNotification, MangoPagination, MangoListView, MangoListWidget,
    MangoTreeView, MangoTreeWidget, MangoTableView, MangoTableWidget,
    MangoLCDNumber, MangoCalendarWidget, MangoStatusBar
)
from mangoui.components.table_list import TableList
from mangoui.models.models import TableColumnModel, TableMenuItemModel
from mangoui.settings.settings import THEME
from mangoui.widgets.input import MangoPushButton, MangoSlider
from mangoui.widgets.layout import MangoGridLayout, MangoVBoxLayout
from mangoui.widgets.window import MangoScrollArea


class DisplayPage(QWidget):
    table_menu = [
        {'name': '编辑', 'action': 'edit'},
        {'name': '删除', 'action': 'delete'}
    ]
    table_column = [
        {'key': 'id', 'name': 'ID', 'width': 7},
        {'key': 'name', 'name': '角色名称', 'width': 300},
        {'key': 'description', 'name': '角色描述', },
        {'key': 'label', 'name': '标签', 'type': 2},
        {'key': 'status', 'name': '状态', 'type': 3},
        {'key': 'ope', 'name': '操作', 'type': 1, 'width': 120},
    ]

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.page = 1
        self.page_size = 20
        self.layout = MangoVBoxLayout(self)
        
        # 创建滚动区域以容纳所有组件
        self.scroll_area = MangoScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = MangoVBoxLayout(self.scroll_widget)
        
        # 标题
        title = QLabel("显示组件展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织显示组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        self.components_grid.setColumnStretch(3, 1)
        
        # 表格组件（原有）
        self.table_column = [TableColumnModel(**i) for i in self.table_column]
        self.table_menu = [TableMenuItemModel(**i) for i in self.table_menu]
        self.table_widget = TableList(self.table_column, self.table_menu, )
        self.table_widget.pagination.click.connect(self.pagination_clicked)
        self.table_widget.clicked.connect(self.callback)
        self.table_widget.table_widget.toggle_click.connect(self.update_data)
        but = MangoPushButton('点击')
        but.clicked.connect(self.batch)
        
        # 将表格组件添加到网格布局中，给它更大的空间
        self.components_grid.addWidget(QLabel("表格组件:"), 0, 0)
        self.components_grid.addWidget(but, 0, 1)
        self.components_grid.addWidget(self.table_widget, 1, 0, 1, 6)  # 占据4列的空间
        self.table_widget.setMinimumHeight(300)  # 设置最小高度

        # 进度条组件
        self.mango_progress_bar = MangoProgressBar()
        self.mango_progress_bar.setValue(75)
        self.components_grid.addWidget(QLabel("进度条:"), 2, 0)
        self.components_grid.addWidget(self.mango_progress_bar, 2, 1)
        
        self.mango_circular_progress = MangoCircularProgress(self)
        self.mango_circular_progress.set_value(80)
        self.components_grid.addWidget(QLabel("圆形进度条:"), 2, 2)
        self.components_grid.addWidget(self.mango_circular_progress, 2, 3)

        # 标签组件
        self.mango_label = MangoLabel("这是一个标签")
        self.components_grid.addWidget(QLabel("标签:"), 3, 0)
        self.components_grid.addWidget(self.mango_label, 3, 1)
        
        self.mango_message = MangoMessage(self, "这是一条消息", THEME.group.info)
        self.components_grid.addWidget(QLabel("消息:"), 3, 2)
        self.components_grid.addWidget(self.mango_message, 3, 3)

        # 通知和分页组件
        self.mango_notification = MangoNotification(self, "这是一条通知", THEME.group.success)
        self.components_grid.addWidget(QLabel("通知:"), 4, 0)
        self.components_grid.addWidget(self.mango_notification, 4, 1)
        
        self.mango_pagination = MangoPagination()
        self.components_grid.addWidget(QLabel("分页:"), 4, 2)
        self.components_grid.addWidget(self.mango_pagination, 4, 3)

        # 列表视图组件
        self.mango_list_view = MangoListView()
        list_model = QStringListModel()
        list_model.setStringList(["项目1", "项目2", "项目3", "项目4", "项目5"])
        self.mango_list_view.setModel(list_model)
        self.components_grid.addWidget(QLabel("列表视图:"), 5, 0)
        self.components_grid.addWidget(self.mango_list_view, 5, 1)
        
        self.mango_list_widget = MangoListWidget()
        for i in range(5):
            self.mango_list_widget.addItem(f"列表项 {i+1}")
        self.components_grid.addWidget(QLabel("列表控件:"), 5, 2)
        self.components_grid.addWidget(self.mango_list_widget, 5, 3)

        # 树形视图组件
        self.mango_tree_view = MangoTreeView()
        tree_model = QStandardItemModel()
        root = QStandardItem("根节点")
        for i in range(3):
            child = QStandardItem(f"子节点 {i+1}")
            for j in range(2):
                sub_child = QStandardItem(f"子节点 {i+1}-{j+1}")
                child.appendRow(sub_child)
            root.appendRow(child)
        tree_model.appendRow(root)
        self.mango_tree_view.setModel(tree_model)
        self.components_grid.addWidget(QLabel("树形视图:"), 6, 0)
        self.components_grid.addWidget(self.mango_tree_view, 6, 1)
        
        self.mango_tree_widget = MangoTreeWidget()
        tree_root = QTreeWidgetItem(self.mango_tree_widget, ["根节点"])
        for i in range(3):
            tree_child = QTreeWidgetItem(tree_root, [f"子节点 {i+1}"])
            for j in range(2):
                QTreeWidgetItem(tree_child, [f"子节点 {i+1}-{j+1}"])
        self.mango_tree_widget.expandAll()
        self.components_grid.addWidget(QLabel("树形控件:"), 6, 2)
        self.components_grid.addWidget(self.mango_tree_widget, 6, 3)

        # 表格视图组件
        self.mango_table_view = MangoTableView()
        table_model = QStandardItemModel(4, 3)
        table_model.setHorizontalHeaderLabels(["列1", "列2", "列3"])
        for i in range(4):
            for j in range(3):
                item = QStandardItem(f"数据 {i+1}-{j+1}")
                table_model.setItem(i, j, item)
        self.mango_table_view.setModel(table_model)
        self.components_grid.addWidget(QLabel("表格视图:"), 7, 0)
        self.components_grid.addWidget(self.mango_table_view, 7, 1)
        
        self.mango_table_widget = MangoTableWidget()
        self.mango_table_widget.setRowCount(4)
        self.mango_table_widget.setColumnCount(3)
        self.mango_table_widget.setHorizontalHeaderLabels(["列1", "列2", "列3"])
        for i in range(4):
            for j in range(3):
                self.mango_table_widget.setItem(i, j, QTableWidgetItem(f"数据 {i+1}-{j+1}"))
        self.components_grid.addWidget(QLabel("表格控件:"), 7, 2)
        self.components_grid.addWidget(self.mango_table_widget, 7, 3)

        # LCD数字显示和日历组件
        self.mango_lcd_number = MangoLCDNumber()
        self.mango_lcd_number.display(1234)
        self.components_grid.addWidget(QLabel("LCD数字显示:"), 8, 0)
        self.components_grid.addWidget(self.mango_lcd_number, 8, 1)
        
        self.mango_calendar_widget = MangoCalendarWidget()
        self.components_grid.addWidget(QLabel("日历控件:"), 8, 2)
        self.components_grid.addWidget(self.mango_calendar_widget, 8, 3)

        # 状态栏组件和滑块组件
        self.mango_status_bar = MangoStatusBar()
        self.mango_status_bar.showMessage("状态信息")
        self.components_grid.addWidget(QLabel("状态栏:"), 9, 0)
        self.components_grid.addWidget(self.mango_status_bar, 9, 1)
        
        self.mango_slider = MangoSlider()
        self.mango_slider.setOrientation(Qt.Horizontal)  # type: ignore
        self.mango_slider.setMinimum(0)
        self.mango_slider.setMaximum(100)
        self.mango_slider.setValue(50)
        self.components_grid.addWidget(QLabel("滑块:"), 9, 2)
        self.components_grid.addWidget(self.mango_slider, 9, 3)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)

    def show_data(self):
        data = []
        for i in range(50):
            data.append({
                "id": i,
                "create_time": "2023-07-13T12:39:57",
                "update_time": "2023-07-13T12:39:57",
                "name": "开发经理",
                "label": f"嘿嘿{i}",
                "status": 1,
                "description": "管理所有开发人员权限"
            })
        self.table_widget.set_data(data, 10)

    def update_data(self, data):
        print(data)

    def pagination_clicked(self, data):
        if data['action'] == 'prev':
            self.page = data['page']
        elif data['action'] == 'next':
            self.page = data['page']
        elif data['action'] == 'per_page':
            self.page_size = data['page']
        self.show_data()

    def callback(self, data):
        action = data.get('action')
        if action and hasattr(self, action):
            if data.get('row'):
                getattr(self, action)(row=data.get('row'))
            else:
                getattr(self, action)()

    def batch(self):
        print(self.table_widget.table_widget.get_selected_items())