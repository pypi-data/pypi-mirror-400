# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-03-07 20:18
# @Author : 毛鹏
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QFrame

from mangoui.settings.settings import THEME


class MangoDashedLine(QWidget):
    def __init__(self, text=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        left_line = QFrame()
        left_line.setFrameShape(QFrame.HLine)
        left_line.setFrameShadow(QFrame.Sunken)
        left_line.setStyleSheet(f"border: 1px dashed {THEME.text_200}; margin: 0; padding: 0;")

        right_line = QFrame()
        right_line.setFrameShape(QFrame.HLine)
        right_line.setFrameShadow(QFrame.Sunken)
        right_line.setStyleSheet(f"border: 1px dashed {THEME.text_200}; margin: 0; padding: 0;")
        if text:
            label = QLabel(text)

            layout.addWidget(left_line, 1)
            layout.addWidget(label)  # 文本居中
            layout.addWidget(right_line, 1)
        else:
            layout.addWidget(left_line)

        # 设置布局
        self.setLayout(layout)