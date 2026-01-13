# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏
import json
from functools import partial
from typing import Optional

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.models.models import *
from mangoui.settings.settings import THEME
from mangoui.widgets.display.mango_label import MangoLabelWidget
from mangoui.widgets.input.mango_toggle import MangoToggle


class MangoTable(QTableWidget):
    click = Signal(object)
    toggle_click = Signal(object)

    def __init__(self, row_column: list[TableColumnModel], row_ope: list[TableMenuItemModel] = None, **kwargs):
        super().__init__()
        self.row_column = row_column
        self.row_ope = row_ope
        self.kwargs = kwargs
        self.column_count = len(row_column)
        self.header_labels = [i.name for i in row_column]
        self.set_stylesheet()
        self.setColumnCount(self.column_count)
        self.setHorizontalHeaderLabels(self.header_labels)
        self.data: Optional[list[dict] | None] = None
        self.set_column_widths()
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)  # type: ignore
        self.setSelectionBehavior(QAbstractItemView.SelectRows)  # type: ignore
        self.verticalHeader().setVisible(False)

        self.setEditTriggers(QTableWidget.NoEditTriggers)  # type: ignore
        self.setMouseTracking(True)

    def set_column_widths(self):
        for index, column in enumerate(self.row_column):
            if column.width:
                self.setColumnWidth(index, column.width)
                self.horizontalHeader().setSectionResizeMode(index, QHeaderView.Fixed)  # type: ignore
            else:
                self.horizontalHeader().setSectionResizeMode(index, QHeaderView.Stretch)  # type: ignore

    def set_value(self, data):
        self.data = data
        self.setRowCount(0)
        if data is None:
            return
        for row_index, row_data in enumerate(data):
            self.insertRow(row_index)
            for column_index, column_data in enumerate(self.row_column):
                if column_data.type == TableTypeEnum.MENU:
                    self.set_menu(row_index, row_data)
                elif column_data.type == TableTypeEnum.TOGGLE:
                    self.set_toggle(row_index, column_data, row_data, column_index)
                elif column_data.type == TableTypeEnum.LABEL:
                    self.set_label(row_index, column_data, row_data, column_index)
                else:
                    self.set_default(row_index, column_data, row_data, column_index)

    def set_default(self, row_index: int, column_data: TableColumnModel, row_data: dict, column_index: int):
        cell_item = row_data[column_data.key]
        if isinstance(cell_item, dict):
            cell_item = cell_item.get(self.kwargs.get('dict_key', 'name'), json.dumps(cell_item, ensure_ascii=False))
        elif isinstance(cell_item, list):
            cell_item = json.dumps(cell_item, ensure_ascii=False)
        if column_data.option is not None:
            cell_item = self.get_option_value(column_data.option, cell_item)
        cell_item = QTableWidgetItem(str(cell_item) if cell_item is not None else '')
        self.setItem(row_index, column_index, cell_item)

    def set_toggle(self, row_index, column_data, row_data, column_index):
        cell_item = row_data[column_data.key]
        mango_toggle = MangoToggle()
        mango_toggle.click.connect(lambda data: self.toggle_click_but(data, row_data))
        mango_toggle.set_value(bool(cell_item))
        container = QWidget()

        layout = QHBoxLayout()
        layout.addWidget(mango_toggle, alignment=Qt.AlignCenter)  # type: ignore
        layout.setContentsMargins(0, 0, 0, 0)  # 去掉边距

        # 将布局设置到容器中
        container.setLayout(layout)

        # 将容器设置为单元格的控件
        self.setCellWidget(row_index, column_index, container)

    def toggle_click_but(self, data, row_data):
        data['row_data'] = row_data
        self.toggle_click.emit(data)

    def set_label(self, row_index, column_data, row_data, column_index):
        cell_item = row_data[column_data.key]
        if isinstance(cell_item, dict):
            cell_item = cell_item.get(self.kwargs.get('dict_key', 'name'), json.dumps(cell_item, ensure_ascii=False))
        elif isinstance(cell_item, list):
            cell_item = json.dumps(cell_item, ensure_ascii=False)
        if column_data.option is not None:
            cell_item = self.get_option_value(column_data.option, cell_item)
        label = MangoLabelWidget(str(cell_item) if cell_item is not None else '')
        self.setCellWidget(row_index, column_index, label)

    def set_menu(self, row, item):
        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        for ope in self.row_ope:
            but = QPushButton(ope.name)
            but.setStyleSheet(
                'QPushButton { background-color: transparent; border: none; padding: 0; color: blue; font-size: 10px; }')
            but.setCursor(QCursor(Qt.PointingHandCursor))  # type: ignore
            action_layout.addWidget(but)
            if not ope.son:
                but.clicked.connect(partial(self.but_clicked, {'action': ope.action, 'row': item}))
            else:
                menu = QMenu()
                for ope1 in ope.son:
                    action = QAction(ope1.name, self)
                    action.triggered.connect(partial(self.but_clicked, {'action': ope1.action, 'row': item}))
                    menu.addAction(action)
                but.clicked.connect(lambda _, m=menu: m.exec_(QCursor.pos()))

        self.setCellWidget(row, len(self.row_column) - 1, action_widget)

    def get_option_value(self, option: list[dict], item1) -> str:
        for i in option:
            if i.get('children'):
                for e in i.get('children'):
                    if e.get('children'):
                        for q in e.get('children'):
                            if q.get('value') == item1:
                                return q.get('label')
                    else:
                        if e.get('value') == item1:
                            return e.get('label')
            if str(i.get('value')) == str(item1):
                return i.get('label')

    def but_clicked(self, data):
        self.click.emit(data)

    def mousePressEvent(self, event):
        local_pos = event.position().toPoint()
        item = self.itemAt(local_pos)
        if item:
            row = item.row()
            self.click.emit({'action': 'click_row', 'row': self.data[row]})
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        local_pos = event.position().toPoint()
        item = self.itemAt(local_pos)
        if item:
            text = item.text()
            rect = self.visualItemRect(item)
            if self.fontMetrics().horizontalAdvance(text) + 20 > rect.width():
                QToolTip.showText(QCursor.pos(), text)
            else:
                QToolTip.hideText()
        else:
            QToolTip.hideText()
        super().mouseMoveEvent(event)

    def get_selected_items(self):
        selected_items = []
        for row in range(self.rowCount()):
            if self.item(row, 1).isSelected():
                content_item = self.item(row, 0)
                selected_items.append(content_item.text())
        return selected_items

    def set_stylesheet(self):
        style = f'''
            /* QTableWidget */
            QTableWidget {{
                background-color: {THEME.bg_100};
                padding: 0px;
                border-radius: {THEME.border_radius};
                gridline-color: transparent;
                color: {THEME.text_100};
                border: 1px solid {THEME.bg_300};
                alternate-background-color: {THEME.bg_200};
            }}
            
            QTableWidget::item {{
                border: none;
                padding: 8px 10px;
                border-bottom: 1px solid {THEME.bg_300};
            }}
            
            QTableWidget::item:selected {{
                background-color: {THEME.primary_200};
                color: {THEME.text_100};
            }}
            
            QTableWidget::item:focus {{
                background-color: {THEME.primary_300};
            }}

            /* Header Sections */
            QHeaderView {{
                background-color: {THEME.bg_100};
                border: none;
            }}
            
            QHeaderView::section {{
                background-color: {THEME.primary_100};
                color: white;
                border: none;
                border-right: 1px solid {THEME.primary_200};
                padding: 10px;
                font-weight: 500;
                font-size: {THEME.font.text_size + 1}px;
            }}
            
            QHeaderView::section:last {{
                border-right: none;
            }}
            
            QHeaderView::section:horizontal {{
                border-top-left-radius: {THEME.border_radius};
                border-top-right-radius: {THEME.border_radius};
            }}
            
            QHeaderView::section:vertical {{
                border-bottom: 1px solid {THEME.bg_300};
            }}

            /* Table Corner Button */
            QTableWidget QTableCornerButton::section {{
                border: none;
                background-color: {THEME.primary_100};
                border-top-left-radius: {THEME.border_radius};
            }}

            /* ScrollBars */
            QScrollBar:horizontal {{
                border: none;
                background: {THEME.bg_200};
                height: 10px;
                margin: 0px 21px 0 21px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {THEME.bg_300};
                min-width: 25px;
                border-radius: 5px;
            }}
            
            QScrollBar::add-line:horizontal {{
                border: none;
                background: {THEME.bg_300};
                width: 20px;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                subcontrol-position: right;
                subcontrol-origin: margin;
            }}
            
            QScrollBar::sub-line:horizontal {{
                border: none;
                background: {THEME.accent_100};
                width: 20px;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
                subcontrol-position: left;
                subcontrol-origin: margin;
            }}
            
            QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {{
                background: none;
            }}
            
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}

            QScrollBar:vertical {{
                border: none;
                background: {THEME.bg_200};
                width: 10px;
                margin: 21px 0 21px 0;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {THEME.bg_300};
                min-height: 25px;
                border-radius: 5px;
            }}
            
            QScrollBar::add-line:vertical {{
                border: none;
                background: {THEME.bg_300};
                height: 20px;
                border-bottom-left-radius: 5px;
                border-bottom-right-radius: 5px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }}
            
            QScrollBar::sub-line:vertical {{
                border: none;
                background: {THEME.bg_300};
                height: 20px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }}
            
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{
                background: none;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        '''
        self.setStyleSheet(style)
