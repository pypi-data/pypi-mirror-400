# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME
from mangoui.widgets.display.mango_label import MangoLabel


class PagesWindow:

    def __init__(self, parent, content_area_left_frame, page_dict):
        self.parent = parent
        self.content_area_left_frame = content_area_left_frame
        self.page_dict = page_dict

        self.loading_indicator = MangoLabel("数据加载中...")
        self.loading_indicator.setAlignment(Qt.AlignCenter)  # type: ignore
        self.loading_indicator.setStyleSheet(f"font-size: 16px; color: {THEME.bg_100};")

        self.main_pages_layout = QVBoxLayout(self.content_area_left_frame)
        self.main_pages_layout.setSpacing(0)
        self.main_pages_layout.setContentsMargins(0, 0, 0, 0)
        self.main_pages_layout.setAlignment(Qt.AlignTop)  # type: ignore
        self.pages = QStackedWidget(self.content_area_left_frame)
        self.pages.setStyleSheet("background-color: #ffffff; border: none;")
        self.main_pages_layout.addWidget(self.pages)
        QMetaObject.connectSlotsByName(self.content_area_left_frame)

    def set_page(self, page: str, data: dict | None = None):
        page_class = self.page_dict.get(page)
        if page_class is not None:
            page = page_class(self.parent)
        else:
            return
        page.data = data if data is not None and isinstance(data, dict) else {}
        if hasattr(page, 'show_data'):
            page.show_data()
        self.pages.addWidget(page)
        self.pages.setCurrentWidget(page)
        self.parent.page = page