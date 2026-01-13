# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-10-29 11:25
# @Author : 毛鹏
from typing import Optional

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.models.models import TreeModel
from mangoui.settings.settings import THEME


class MangoTree(QTreeWidget):
    clicked = Signal(TreeModel)

    def __init__(self,
                 title: str,
                 parent=None):
        super().__init__(parent)
        self.data: Optional[list[TreeModel] | None] = None
        self.setHeaderLabels([title])
        self.itemClicked.connect(self.on_item_clicked)
        self.set_stylesheet()

    def on_item_clicked(self, item, column):
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())
        else:
            self.clicked.emit(item.data(0, Qt.UserRole))  # type: ignore

    def set_item(self, items: list[TreeModel]):
        self.data = items
        for item in items:
            parent_item = QTreeWidgetItem(self)
            parent_item.setText(0, item.title)
            parent_item.setData(0, Qt.UserRole, item)  # type: ignore
            if item.children:
                for i in item.children:
                    child_item = QTreeWidgetItem(parent_item)
                    child_item.setText(0, i.title)  # type: ignore
                    child_item.setData(0, Qt.UserRole, i)  # type: ignore

    def clear_items(self):
        self.clear()
        self.data = None

    def set_stylesheet(self):
        style = f"""
            MangoTree {{
                background-color: {THEME.bg_100};
                border-radius: {THEME.border_radius};
                border: 1px solid {THEME.bg_300};
                color: {THEME.text_100};
            }}
        
            MangoTree::item {{
                padding: 5px;
                background-color: {THEME.bg_100};
                color: {THEME.text_100};
            }}
        
            MangoTree::item:selected {{
                background-color: {THEME.bg_100};
                color: {THEME.text_100};
            }}
        
            MangoTree::item:hover {{
                background-color: {THEME.primary_200};
            }}
            QHeaderView {{
                font-size: 14px;  /* 修改字体大小 */

            }}
        """
        self.setStyleSheet(style)
