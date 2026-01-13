# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-08-24 17:08
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoLabel(QLabel):
    def __init__(self, text=None, parent=None, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.kwargs = kwargs
        self.set_style()
        self.setText(str(text) if text is not None else '')

        # 启用右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def set_style(self, style=""):
        # 如果用户提供了自定义样式，则使用它
        if 'style' in self.kwargs and self.kwargs['style']:
            style = self.kwargs.get('style', style)
        else:
            # 否则使用默认样式
            style = f"""
            QLabel {{
                color: {THEME.text_100};
                background-color: transparent;
                font-family: {THEME.font.family};
                font-size: {THEME.font.text_size}px;
                font-weight: normal;  /* 去除加粗效果 */
                padding: 2px;
            }}
            """
        self.setStyleSheet(style)

    def show_context_menu(self, position):
        """显示右键上下文菜单"""
        context_menu = QMenu(self)
        # 删除了固定的菜单大小设置，让菜单根据内容自动调整大小
        context_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {THEME.bg_100}; 
                border-radius: {THEME.border_radius};
                padding: 4px;
                border: 1px solid {THEME.bg_300};
                background-clip: border;
                min-width: 80px;  /* 设置最小宽度确保文字能完整显示 */
            }}
            QMenu::item {{
                padding: 6px 20px;
                margin: 2px;
                border-radius: 4px;
                background-color: transparent;
                color: {THEME.text_100};
            }}
            QMenu::item:selected {{
                background-color: {THEME.primary_200};
                color: {THEME.text_100};
            }}
        """)

        # 设置窗口标志，避免系统默认的菜单样式
        context_menu.setWindowFlags(context_menu.windowFlags() | Qt.FramelessWindowHint)
        context_menu.setAttribute(Qt.WA_TranslucentBackground)

        # 创建复制动作
        copy_action = QAction("复制", self)  # 删除了前面多余的空格
        copy_action.triggered.connect(self.copy_text)
        context_menu.addAction(copy_action)

        context_menu.exec_(self.mapToGlobal(position))
        
    def copy_text(self):
        """复制文本到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text())
        from mangoui.components import success_message
        success_message(self.parent or self, '复制成功')




class MangoLabelWidget(QWidget):

    def __init__(self, text=None, parent=None, **kwargs):
        super().__init__(parent)
        self.kwargs = kwargs

        self.kwargs['style'] = f"""
            QLabel {{
                color: {THEME.text_100};
                background-color: {kwargs.get('background_color', THEME.primary_100)};
                padding: 6px 12px;
                border: 1px solid #e0e0e0;  /* 使用固定浅色边框 */
                border-radius: {THEME.border_radius};
                font-family: {THEME.font.family};
                font-size: {THEME.font.text_size}px;
                font-weight: normal;  /* 去除加粗效果 */
            }}
        """

        self.setMaximumHeight(25)
        self.mango_label = MangoLabel(text=text, parent=self, **self.kwargs)
        self.mango_label.setAlignment(Qt.AlignCenter)  # type: ignore

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)  # type: ignore
        layout.addWidget(self.mango_label, alignment=Qt.AlignCenter)  # type: ignore
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)