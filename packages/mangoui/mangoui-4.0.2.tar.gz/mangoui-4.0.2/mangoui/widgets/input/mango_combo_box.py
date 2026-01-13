# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-04 17:32
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.models.models import ComboBoxDataModel, DialogCallbackModel
from mangoui.settings.settings import THEME


class MangoComboBoxMany(QComboBox):
    click = Signal(object)

    def __init__(self,
                 placeholder: str,
                 data: list[ComboBoxDataModel],
                 value: str = None,
                 parent=None):
        super().__init__(parent)
        self.dialog = None
        self.data = data
        self.parent = parent

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.list_widget = QListWidget()
        self.list_widget.setContentsMargins(0, 0, 0, 0)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.list_widget)
        self.populate_list_widget()
        if placeholder:
            self.lineEdit().setPlaceholderText(placeholder)
            # 设置默认选项
        if value is not None:
            self.set_value(value)
        self.set_stylesheet()

    def populate_list_widget(self):
        for option in self.data:
            item = QListWidgetItem(option.name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)  # type: ignore
            item.setCheckState(Qt.Unchecked)  # type: ignore
            self.list_widget.addItem(item)

    def showPopup(self):
        if self.dialog is None:
            self.dialog = QDialog(self)
        else:
            self.dialog.setWindowTitle("选择项目")
            self.dialog.setFixedSize(200, 150)
            self.dialog.setLayout(self.layout)
            self.list_widget.itemChanged.connect(self.update_display)
            self.dialog.accepted.connect(self.update_display)
            self.dialog.exec()

    def update_display(self):
        selected_items = [self.list_widget.item(i).text() for i in range(self.list_widget.count()) if
                          self.list_widget.item(i).checkState() == Qt.Checked]  # type: ignore
        if selected_items:
            self.lineEdit().setText(", ".join(selected_items))
        else:
            self.lineEdit().clear()
            self.lineEdit().setPlaceholderText("选择项目")

    def get_value(self):
        return [self.list_widget.item(i).text() for i in range(self.list_widget.count()) if
                self.list_widget.item(i).checkState() == Qt.Checked]  # type: ignore

    def set_value(self, value):
        try:
            value_list = eval(value) if isinstance(value, str) else value
        except Exception:
            value_list = [value]
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.text() in value_list:
                item.setCheckState(Qt.Checked)  # type: ignore
            else:
                item.setCheckState(Qt.Unchecked)  # type: ignore
        selected_values = [item.text() for i in range(self.list_widget.count()) if
                           self.list_widget.item(i).checkState() == Qt.Checked]  # type: ignore
        if selected_values:
            self.lineEdit().setText(", ".join(selected_values))
        else:
            self.lineEdit().clear()
            self.lineEdit().setPlaceholderText("选择项目")

        self.update_display()

    def set_stylesheet(self, icon=':/icons/down.svg'):
        style = f'''
        QComboBox {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_200};
            padding: 8px 12px;
            padding-right: 35px; /* 为下拉箭头留出更多空间 */
            selection-color: white;
            selection-background-color: {THEME.primary_100};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            outline: none;
        }}
        
        QComboBox:focus {{
            border: 1px solid {THEME.primary_100};
            background-color: {THEME.bg_100};
        }}
        
        QComboBox:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: {THEME.bg_200};
            border-left-style: solid;
            border-top-right-radius: {THEME.border_radius};
            border-bottom-right-radius: {THEME.border_radius};
        }}
        
        QComboBox::down-arrow {{
            image: url({icon});
            width: 20px;
            height: 20px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {THEME.bg_100};
            border: 1px solid {THEME.bg_200};
            border-radius: {THEME.border_radius};
            selection-background-color: {THEME.primary_200};
            selection-color: {THEME.text_100};
            outline: none;
        }}
        
        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            color: {THEME.text_100};
        }}
        
        QComboBox QAbstractItemView::item:selected {
            background-color: {THEME.primary_200};
            color: {THEME.text_100};
        }
        
        /* 滚动条样式 - 与 MangoScrollArea 保持一致 */
        QComboBox QAbstractItemView QScrollBar:vertical {
            border: none;
            background: {THEME.bg_300};
            width: 8px;
            margin: 21px 0;
            border-radius: 0px;
        }
        
        QComboBox QAbstractItemView QScrollBar::handle:vertical {
            background: {THEME.bg_300};
            min-height: 25px;
            border-radius: 4px;
        }
        
        QComboBox QAbstractItemView QScrollBar::add-line:vertical {
            border: none;
            background: {THEME.bg_300};
            height: 20px;
            border-bottom-left-radius: 4px;
            border-bottom-right-radius: 4px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }
        
        QComboBox QAbstractItemView QScrollBar::sub-line:vertical {
            border: none;
            background: {THEME.bg_300};
            height: 20px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        
        QComboBox QAbstractItemView QScrollBar:horizontal {
            border: none;
            background: {THEME.bg_300};
            height: 8px;
            margin: 0px 21px;
            border-radius: 0px;
        }
        
        QComboBox QAbstractItemView QScrollBar::handle:horizontal {
            background: {THEME.bg_300};
            min-width: 25px;
            border-radius: 4px;
        }
        
        QComboBox QAbstractItemView QScrollBar::add-line:horizontal {
            border: none;
            background: {THEME.bg_300};
            width: 20px;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }
        
        QComboBox QAbstractItemView QScrollBar::sub-line:horizontal {
            border: none;
            background: {THEME.bg_300};
            width: 20px;
            border-top-left-radius: 4px;
            border-bottom-left-radius: 4px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }
        '''
        self.setStyleSheet(style)
        self.setMinimumHeight(36)  # 设置最小高度


class MangoComboBox(QComboBox):
    click = Signal(object)
    # 选择框

    def __init__(
            self,
            placeholder: str,
            data: list[ComboBoxDataModel],
            value: int | str = None,
            subordinate: str | None = None,
            is_form: bool = True,
            **kwargs,
    ):
        super().__init__()
        self.kwargs = kwargs
        self.placeholder = placeholder
        self.data = data
        self.value = value
        self.subordinate = subordinate
        self.is_form = is_form
        # 设置样式表
        self.set_stylesheet()
        self.currentIndexChanged.connect(self.combo_box_changed)
        self.set_select(self.data)
        self.setCurrentIndex(-1)
        self.set_value(self.value)
        if self.placeholder:
            self.setPlaceholderText(self.placeholder)

    def get_value(self):
        value = self.currentText()
        if self.data:
            data_dict = {item.name: item.id for item in self.data}
            return data_dict.get(value)

    def set_select(self, data: list[ComboBoxDataModel], clear: bool = False):
        if clear:
            self.clear()
        if data:
            self.data = data
            self.addItems([i.name for i in data])

    def set_value(self, value: str):
        if value is not None and value != '':
            for i in self.data:
                if i.id == str(value):
                    self.value = value
                    self.setCurrentText(i.name)
                    break
            else:
                self.value = ''
                self.setCurrentText('')
        elif value == '':
            self.value = ''
            self.setCurrentText('')

    def combo_box_changed(self, data):
        if self.is_form:
            if self.subordinate:
                self.click.emit(DialogCallbackModel(
                    key=self.kwargs.get('key'),
                    value=self.get_value(),
                    subordinate=self.subordinate,
                    input_object=self
                ))
        else:
            self.click.emit(self.get_value())

    def set_stylesheet(self, icon=':/icons/down.svg'):
        style = f'''
        QComboBox {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            padding: 8px 12px;
            padding-right: 35px; /* 为下拉箭头留出更多空间 */
            selection-color: white;
            selection-background-color: {THEME.primary_100};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            outline: none;
        }}
        
        QComboBox:focus {{
            border: 1px solid {THEME.primary_100};
            background-color: {THEME.bg_100};
        }}
        
        QComboBox:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left-width: 1px;
            border-left-color: {THEME.bg_300};
            border-left-style: solid;
            border-top-right-radius: {THEME.border_radius};
            border-bottom-right-radius: {THEME.border_radius};
        }}
        
        QComboBox::down-arrow {{
            image: url({icon});
            width: 20px;
            height: 20px;
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
            padding: 8px 12px;
            color: {THEME.text_100};
        }}
        
        QComboBox QAbstractItemView::item:selected {{
            background-color: {THEME.primary_200};
            color: {THEME.text_100};
        }}
        
        /* 滚动条样式 - 与 MangoScrollArea 保持一致 */
        QComboBox QAbstractItemView QScrollBar:vertical {{
            border: none;
            background: {THEME.bg_300};
            width: 8px;
            margin: 21px 0;
            border-radius: 0px;
        }}
        
        QComboBox QAbstractItemView QScrollBar::handle:vertical {{
            background: {THEME.bg_300};
            min-height: 25px;
            border-radius: 4px;
        }}
        
        QComboBox QAbstractItemView QScrollBar::add-line:vertical {{
            border: none;
            background: {THEME.bg_300};
            height: 20px;
            border-bottom-left-radius: 4px;
            border-bottom-right-radius: 4px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }}
        
        QComboBox QAbstractItemView QScrollBar::sub-line:vertical {{
            border: none;
            background: {THEME.bg_300};
            height: 20px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }}
        
        QComboBox QAbstractItemView QScrollBar:horizontal {{
            border: none;
            background: {THEME.bg_300};
            height: 8px;
            margin: 0px 21px;
            border-radius: 0px;
        }}
        
        QComboBox QAbstractItemView QScrollBar::handle:horizontal {{
            background: {THEME.bg_300};
            min-width: 25px;
            border-radius: 4px;
        }}
        
        QComboBox QAbstractItemView QScrollBar::add-line:horizontal {{
            border: none;
            background: {THEME.bg_300};
            width: 20px;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }}
        
        QComboBox QAbstractItemView QScrollBar::sub-line:horizontal {{
            border: none;
            background: {THEME.bg_300};
            width: 20px;
            border-top-left-radius: 4px;
            border-bottom-left-radius: 4px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }}
        '''
        self.setStyleSheet(style)
        self.setMinimumHeight(36)  # 设置最小高度
