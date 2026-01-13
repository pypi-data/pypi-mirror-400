# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 树形视图组件
# @Time   : 2025-11-25 10:25
# @Author : Qwen

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from mangoui.settings.settings import THEME


class MangoTreeView(QTreeView):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QTreeView {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            outline: none;
            padding: 2px;
        }}

        QTreeView::item {{
            padding: 4px;
            border-radius: {THEME.border_radius};
        }}

        QTreeView::item:selected {{
            background-color: {THEME.primary_100};
            color: white;
        }}

        QTreeView::item:hover {{
            background-color: {THEME.bg_200};
        }}

        QTreeView::item:selected:hover {{
            background-color: {THEME.primary_200};
        }}

        QTreeView:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        
        QTreeView::branch:has-siblings:!adjoins-item {{
            border-image: url(:/icons/vline.svg) 0;
        }}

        QTreeView::branch:has-siblings:adjoins-item {{
            border-image: url(:/icons/branch_more.svg) 0;
        }}

        QTreeView::branch:!has-children:!has-siblings:adjoins-item {{
            border-image: url(:/icons/branch_end.svg) 0;
        }}

        QTreeView::branch:has-children:!has-siblings:closed,
        QTreeView::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: url(:/icons/icon_arrow_right.svg);
        }}

        QTreeView::branch:open:has-children:!has-siblings,
        QTreeView::branch:open:has-children:has-siblings {{
            border-image: none;
            image: url(:/icons/down.svg);
        }}
        
        QTreeView QScrollBar:vertical {{
            border: none;
            background: {THEME.bg_300};
            width: 8px;
            margin: 0px 0px 0px 0px;
            border-radius: 0px;
        }}
        
        QTreeView QScrollBar::handle:vertical {{
            background: {THEME.bg_300};
            min-height: 25px;
            border-radius: 4px;
        }}
        """
        self.setStyleSheet(style)


class MangoTreeWidget(QTreeWidget):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs
        self.set_stylesheet()
        
    def set_stylesheet(self):
        style = f"""
        QTreeWidget {{
            background-color: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            outline: none;
            padding: 2px;
        }}

        QTreeWidget::item {{
            padding: 4px;
            border-radius: {THEME.border_radius};
        }}

        QTreeWidget::item:selected {{
            background-color: {THEME.primary_100};
            color: white;
        }}

        QTreeWidget::item:hover {{
            background-color: {THEME.bg_200};
        }}

        QTreeWidget::item:selected:hover {{
            background-color: {THEME.primary_200};
        }}

        QTreeWidget:disabled {{
            background-color: {THEME.bg_200};
            color: {THEME.text_200};
        }}
        
        QTreeWidget::branch:has-siblings:!adjoins-item {{
            border-image: url(:/icons/vline.svg) 0;
        }}

        QTreeWidget::branch:has-siblings:adjoins-item {{
            border-image: url(:/icons/branch_more.svg) 0;
        }}

        QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {{
            border-image: url(:/icons/branch_end.svg) 0;
        }}

        QTreeWidget::branch:has-children:!has-siblings:closed,
        QTreeWidget::branch:closed:has-children:has-siblings {{
            border-image: none;
            image: url(:/icons/arrow_right.svg);
        }}

        QTreeWidget::branch:open:has-children:!has-siblings,
        QTreeWidget::branch:open:has-children:has-siblings {{
            border-image: none;
            image: url(:/icons/down.svg);
        }}
        
        QTreeWidget QScrollBar:vertical {{
            border: none;
            background: {THEME.bg_300};
            width: 8px;
            margin: 0px 0px 0px 0px;
            border-radius: 0px;
        }}
        
        QTreeWidget QScrollBar::handle:vertical {{
            background: {THEME.bg_300};
            min-height: 25px;
            border-radius: 4px;
        }}
        """
        self.setStyleSheet(style)