# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-10-14 17:30
# @Author : 毛鹏
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout

from mangoui.settings.settings import THEME


class MangoTabs(QTabWidget):
    clicked = Signal(str)

    def __init__(self):
        super().__init__()
        self.previous_index = 0
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet(f"""
            QTabWidget {{
                background-color: {THEME.bg_100};
                border-radius: {THEME.border_radius};
            }}
            
            QTabBar {{
                background: transparent;
                border-bottom: 2px solid {THEME.bg_200};
                spacing: 4px;
                qproperty-drawBase: 0; /* 隐藏默认底线 */
            }}
            
            QTabBar::tab {{
                background: transparent;
                border: none;
                padding: 10px 20px;
                margin: 0 2px;
                color: {THEME.text_200};
                font-family: {THEME.font.family};
                font-size: {THEME.font.text_size}px;
                border-top-left-radius: {THEME.border_radius};
                border-top-right-radius: {THEME.border_radius};
            }}
            
            QTabBar::tab:selected {{
                color: {THEME.text_100};
                background-color: {THEME.bg_100};
                border-bottom: 2px solid {THEME.primary_100};
                font-weight: 600;
            }}
            
            QTabBar::tab:hover {{
                color: {THEME.text_100};
                background-color: {THEME.bg_200};
            }}
            
            QTabBar::tab:selected:hover {{
                background-color: {THEME.bg_100};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {THEME.bg_300};
                border-top: none;
                padding: 16px;
                border-radius: 0 0 {THEME.border_radius} {THEME.border_radius};
                background-color: {THEME.bg_100};
            }}
            
            QTabBar::close-button {{
                image: url(:/icons/icon_close.svg);
                subcontrol-position: right;
                padding: 4px;
                border-radius: 4px;
            }}
            
            QTabBar::close-button:hover {{
                background: {THEME.primary_200};
            }}
        """)

    def add_tab(self, tab_name, widget):
        new_tab = QWidget()
        new_tab.setContentsMargins(0, 0, 0, 0)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 0)
        layout.addWidget(widget)
        new_tab.setLayout(layout)
        self.addTab(new_tab, tab_name)
