# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-10-14 21:13
# @Author : 毛鹏
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QFrame

from mangoui.settings.settings import THEME


class MangoScrollArea(QScrollArea):

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.kwargs = kwargs
        self.setFrameShape(QFrame.NoFrame)  # type: ignore
        if self.kwargs.get('vertical_off'):
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore
        if self.kwargs.get('horizontal_off'):
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # type: ignore
        self.setWidgetResizable(True)

        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet(u"background: transparent;")
        self.setWidget(self.scroll_widget)
        self.layout = QVBoxLayout(self.scroll_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_widget.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignTop)  # type: ignore

        self.set_style()

    def set_style(self):
        self.setStyleSheet(f"""
        QScrollArea {{
            background: transparent;
            {f'background-color: {self.kwargs.get("background_color")};' if self.kwargs.get("background_color") else ''}
            padding: 5px;
            border-radius: {THEME.border_radius}px;
            {f'border: 1px solid {self.kwargs.get("border")};' if self.kwargs.get('border') else ''}
        }}
        
        QScrollBar:horizontal {{
            border: none;
            background: {THEME.bg_300};
            height: 8px;
            margin: 0px 21px;
            border-radius: 0px;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {THEME.bg_300};
            min-width: 25px;
            border-radius: 4px;
        }}
        
        QScrollBar::add-line:horizontal {{
            border: none;
            background: {THEME.bg_300};
            width: 20px;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }}
        
        QScrollBar::sub-line:horizontal {{
            border: none;
            background: {THEME.bg_300};
            width: 20px;
            border-top-left-radius: 4px;
            border-bottom-left-radius: 4px;
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
            background: {THEME.bg_300};
            width: 8px;
            margin: 21px 0;
            border-radius: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {THEME.bg_300};
            min-height: 25px;
            border-radius: 4px;
        }}
        
        QScrollBar::add-line:vertical {{
            border: none;
            background: {THEME.bg_300};
            height: 20px;
            border-bottom-left-radius: 4px;
            border-bottom-right-radius: 4px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }}
        
        QScrollBar::sub-line:vertical {{
            border: none;
            background: {THEME.bg_300};
            height: 20px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }}

        """)