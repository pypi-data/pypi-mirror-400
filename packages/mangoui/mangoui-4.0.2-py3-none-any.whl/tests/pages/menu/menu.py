# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-02 21:24
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# 从具体的组件模块中导入所需的组件
from mangoui.widgets.menu import (
    MangoTabs, MangoMenuBar, MangoToolBar
)
from mangoui.widgets.layout import MangoVBoxLayout, MangoGridLayout


class MenuPage(QWidget):
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
        title = QLabel("菜单组件展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织菜单组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        
        # 选项卡组件（原有）
        self.mango_tabs = MangoTabs()
        self.mango_tabs.add_tab("标签页1", QLabel("标签页1内容"))
        self.mango_tabs.add_tab("标签页2", QLabel("标签页2内容"))
        self.mango_tabs.add_tab("标签页3", QLabel("标签页3内容"))
        self.components_grid.addWidget(QLabel("选项卡:"), 0, 0)
        self.components_grid.addWidget(self.mango_tabs, 0, 1)

        # 菜单栏组件
        self.mango_menu_bar = MangoMenuBar()
        file_menu = self.mango_menu_bar.addMenu("文件")
        edit_menu = self.mango_menu_bar.addMenu("编辑")
        help_menu = self.mango_menu_bar.addMenu("帮助")
        
        # 文件菜单项
        new_action = file_menu.addAction("新建")
        open_action = file_menu.addAction("打开")
        save_action = file_menu.addAction("保存")
        file_menu.addSeparator()
        exit_action = file_menu.addAction("退出")
        
        # 编辑菜单项
        undo_action = edit_menu.addAction("撤销")
        redo_action = edit_menu.addAction("重做")
        edit_menu.addSeparator()
        cut_action = edit_menu.addAction("剪切")
        copy_action = edit_menu.addAction("复制")
        paste_action = edit_menu.addAction("粘贴")
        
        # 帮助菜单项
        about_action = help_menu.addAction("关于")
        
        self.components_grid.addWidget(QLabel("菜单栏:"), 1, 0)
        self.components_grid.addWidget(self.mango_menu_bar, 1, 1)

        # 工具栏组件
        self.mango_tool_bar = MangoToolBar("工具栏")
        self.mango_tool_bar.addAction("新建", lambda: print("新建"))
        self.mango_tool_bar.addAction("打开", lambda: print("打开"))
        self.mango_tool_bar.addAction("保存", lambda: print("保存"))
        self.mango_tool_bar.addSeparator()
        self.mango_tool_bar.addAction("剪切", lambda: print("剪切"))
        self.mango_tool_bar.addAction("复制", lambda: print("复制"))
        self.mango_tool_bar.addAction("粘贴", lambda: print("粘贴"))
        
        self.components_grid.addWidget(QLabel("工具栏:"), 2, 0)
        self.components_grid.addWidget(self.mango_tool_bar, 2, 1)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)