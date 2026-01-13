# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏
import math

from PySide6.QtCore import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoPagination(QWidget):
    click = Signal(object)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.total_size = 0
        self.page = 1
        self.number_part = 20

        self.current_page_label1 = QLabel(f"共 {self.total_size} 条")

        self.prev_icon_button = QPushButton()
        self.prev_icon_button.setMaximumWidth(36)
        self.prev_icon_button.setMinimumHeight(36)
        self.prev_icon_button.setEnabled(False)
        self.prev_icon_button.setText('<')
        self.prev_icon_button.setCursor(Qt.PointingHandCursor)  # type: ignore

        self.next_icon_button = QPushButton()
        self.next_icon_button.setMaximumWidth(36)
        self.next_icon_button.setMinimumHeight(36)
        self.next_icon_button.setText('>')
        self.next_icon_button.setCursor(Qt.PointingHandCursor)  # type: ignore

        # 创建当前页显示的标签
        self.current_page_label = QLabel(f"{self.page}")
        self.current_page_label.setStyleSheet(f"""
            QLabel {{
                color: {THEME.text_100};
                font-family: {THEME.font.family};
                font-size: {THEME.font.text_size}px;
                font-weight: 500;
                padding: 0 8px;
            }}
        """)
        
        self.items_per_page_combo = QComboBox()
        self.items_per_page_combo.addItems(["10 条/页", "20 条/页", "30 条/页", "50 条/页", "100 条/页"])
        self.items_per_page_combo.setCurrentText("20 条/页")
        self.items_per_page_combo.setCursor(Qt.PointingHandCursor)  # type: ignore

        # 布局设置
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(self.current_page_label1)
        layout.addWidget(self.prev_icon_button)
        layout.addWidget(self.current_page_label)
        layout.addWidget(self.next_icon_button)
        layout.addWidget(self.items_per_page_combo)

        self.setLayout(layout)
        
        # 设置样式
        self.set_stylesheet()

        self.prev_icon_button.clicked.connect(self.on_prev_page)
        self.next_icon_button.clicked.connect(self.on_next_page)

        self.items_per_page_combo.currentIndexChanged.connect(self.on_items_per_page_changed)
        self.button_enabled()

    def on_prev_page(self):
        self.page -= 1
        self.click.emit({'action': 'prev', 'page': self.page})
        self.current_page_label.setText(str(self.page))
        self.button_enabled()

    def on_next_page(self):
        self.page += 1
        self.click.emit({'action': 'next', 'page': self.page})
        self.current_page_label.setText(str(self.page))
        self.button_enabled()

    def on_items_per_page_changed(self, index):
        selected_text = self.items_per_page_combo.itemText(index)
        self.number_part = int(selected_text.split(" ")[0])
        self.click.emit({'action': 'per_page', 'page': self.number_part})
        self.button_enabled()

    def set_total_size(self, total_size: str):
        self.current_page_label1.setText(f"共 {total_size} 条")
        if total_size:
            self.total_size = int(total_size)
        self.button_enabled()

    def button_enabled(self):
        if self.page > 1:
            self.prev_icon_button.setEnabled(True)
        else:
            self.prev_icon_button.setEnabled(False)
        if self.page >= math.ceil(self.total_size / self.number_part):
            self.next_icon_button.setEnabled(False)
        else:
            self.next_icon_button.setEnabled(True)
            
    def set_stylesheet(self):
        # 设置按钮样式
        button_style = f"""
        QPushButton {{
            background-color: {THEME.bg_100};
            border: 1px solid {THEME.bg_300};
            border-radius: {THEME.border_radius};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            font-weight: 500;
            padding: 6px 12px;
        }}
        QPushButton:hover {{
            background-color: {THEME.primary_200};
            border: 1px solid {THEME.primary_100};
        }}
        QPushButton:pressed {{
            background-color: {THEME.primary_300};
        }}
        QPushButton:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
            border: 1px solid {THEME.bg_300};
        }}
        """
        
        self.prev_icon_button.setStyleSheet(button_style)
        self.next_icon_button.setStyleSheet(button_style)
        
        # 设置标签样式
        label_style = f"""
        QLabel {{
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            padding: 0 8px;
        }}
        """
        
        self.current_page_label1.setStyleSheet(label_style)
        
        # 设置下拉框样式
        combo_style = f"""
        QComboBox {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            padding: 6px 12px;
            padding-right: 30px;
            selection-color: white;
            selection-background-color: {THEME.primary_100};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            outline: none;
            min-width: 100px;
        }}
        
        QComboBox:focus {{
            border: 1px solid {THEME.primary_100};
        }}
        
        QComboBox::drop-down {{
            border: none;
            background-color: transparent;
            width: 20px;
            height: 20px;
            right: 6px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {THEME.bg_100};
            border: 1px solid {THEME.bg_300};
            border-radius: {THEME.border_radius};
            selection-background-color: {THEME.primary_200};
            selection-color: {THEME.text_100};
            outline: none;
        }}
        
        QComboBox QAbstractItemView::item {{
            padding: 6px 12px;
            color: {THEME.text_100};
        }}
        
        QComboBox QAbstractItemView::item:selected {{
            background-color: {THEME.primary_200};
        }}
        """
        
        self.items_per_page_combo.setStyleSheet(combo_style)
