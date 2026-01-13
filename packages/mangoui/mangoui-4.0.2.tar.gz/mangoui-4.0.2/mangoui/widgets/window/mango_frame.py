# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoFrame(QFrame):

    def __init__(
            self,
            parent,
            layout=Qt.Vertical,  # type: ignore
            margin=0,
            spacing=2,
            text_font="9pt 'Segoe UI'",
            enable_shadow=True
    ):
        super().__init__()
        self.parent = parent
        self._layout_type = layout  # 保存布局类型参数，避免与 layout() 方法冲突
        self.margin = margin
        self.text_font = text_font
        self.enable_shadow = enable_shadow

        self.setObjectName("pod_bg_app")
        self.set_stylesheet()

        # 先检查是否有现有布局，如果有则先删除（在创建 self.layout 之前检查，避免覆盖 layout() 方法）
        existing_layout = super().layout()
        if existing_layout is not None:
            # 清空现有布局的所有项目
            while existing_layout.count():
                item = existing_layout.takeAt(0)
                if item:
                    del item
            # 删除现有布局
            existing_layout.setParent(None)

        # 创建新布局（不传入 widget，避免自动设置布局）
        if layout == Qt.Vertical:  # type: ignore
            self.layout = QHBoxLayout()
        else:
            self.layout = QHBoxLayout()
        self.layout.setContentsMargins(margin, margin, margin, margin)
        self.layout.setSpacing(spacing)
        
        # 设置新布局
        self.setLayout(self.layout)

        if enable_shadow:
            self.shadow = QGraphicsDropShadowEffect()
            self.shadow.setBlurRadius(20)
            self.shadow.setXOffset(0)
            self.shadow.setYOffset(0)
            self.shadow.setColor(QColor(0, 0, 0, 160))
            self.setGraphicsEffect(self.shadow)

    def set_stylesheet(self, border_radius=None, border_size=None):

        style = f"""
            #pod_bg_app {{
                background-color: {THEME.bg_100};
                border-radius: {THEME.border_radius};
                border: {border_size if border_size else '1'}px solid {border_radius if border_radius else THEME.bg_300};
            }}
            QFrame {{ 
                color: {THEME.text_100};
                font: {self.text_font};
            }}
            """
        self.setStyleSheet(style)
