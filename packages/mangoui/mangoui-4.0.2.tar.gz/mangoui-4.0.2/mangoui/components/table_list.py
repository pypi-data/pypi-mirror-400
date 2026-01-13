from PySide6.QtCore import Signal
from PySide6.QtWidgets import *

from mangoui.models.models import TableColumnModel, TableMenuItemModel
from mangoui.widgets.display import MangoTable, MangoPagination


class TableList(QWidget):
    clicked = Signal(object)
    released = Signal(object)

    def __init__(self, row_column: list[TableColumnModel], row_ope: list[TableMenuItemModel] = None):
        super().__init__()
        self.row_column = row_column
        self.row_ope = row_ope
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.table_widget = MangoTable(row_column, row_ope, )
        self.table_widget.click.connect(self.but_clicked)
        self.layout.addWidget(self.table_widget)
        self.pagination = MangoPagination(self)
        self.layout.addWidget(self.pagination)
        self.setLayout(self.layout)
        self.page_size = 10

    def set_data(self, data, total_size: int | None = None):
        if total_size:
            self.pagination.set_total_size(str(total_size))
        self.table_widget.set_value(data)

    def but_clicked(self, data):
        self.clicked.emit(data)
