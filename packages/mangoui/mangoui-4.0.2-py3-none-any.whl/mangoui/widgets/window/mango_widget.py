# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-05-25 23:31
# @Author : 毛鹏
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QWidget

from mangoui.widgets.layout import MangoVBoxLayout


class DataLoadWorker(QThread):
    finished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        try:
            self.parent.load_page_data()  # type: ignore
        finally:
            self.finished.emit()


class MangoWidget(QWidget):

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.worker = None
        self.layout = MangoVBoxLayout()
        self.setLayout(self.layout)

    def show_data(self):
        if self.worker is not None and self.worker.isRunning():
            return
        self.worker = DataLoadWorker(self)
        self.worker.finished.connect(lambda: setattr(self, 'worker', None))
        self.worker.start()

    def load_page_data(self):
        pass
