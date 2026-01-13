# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoCredits(QWidget):
    update_label = Signal(str)

    def __init__(self, copyright, version, ):
        super().__init__()
        self.copyright = copyright
        self.version = version

        self.widget_layout = QHBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)

        style = f"""
        #bg_frame {{
            border-radius: {THEME.border_radius};
            background-color: {THEME.primary_100};
            border: 1px solid {THEME.bg_300};
            padding: 6px 16px; /* 调整内边距使字体垂直居中 */
        }}
        
        QLabel {{
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
            color: {THEME.text_100};
            padding: 0 8px;
            background: transparent; /* 确保标签背景透明 */
            /* 移除最小高度设置，让标签根据内容自适应高度 */
            /* line-height: 20px; 移除固定行高 */
        }}
        
        QLabel:first-child {{
            font-weight: 500;
        }}
        
        QLabel:last-child {{
            color: {THEME.text_200};
        }}
        """

        self.bg_frame = QFrame()
        self.bg_frame.setObjectName("bg_frame")
        self.bg_frame.setStyleSheet(style)
        # 移除最小高度设置，让组件根据内容自适应高度
        self.bg_frame.setFrameShape(QFrame.NoFrame)  # 确保框架没有边框
        self.bg_frame.setLineWidth(0)  # 确保框架线宽为0

        self.widget_layout.addWidget(self.bg_frame)

        self.bg_layout = QHBoxLayout(self.bg_frame)
        self.bg_layout.setContentsMargins(0, 0, 0, 0)
        self.bg_layout.setSpacing(10)  # 设置控件间距为10像素

        # 创建一个包含版权和版本信息的水平布局
        info_layout = QHBoxLayout()
        info_layout.setSpacing(10)  # 设置标签之间的间距
        info_layout.setContentsMargins(0, 0, 0, 0)

        self.copyright_label = QLabel()
        self.copyright_label.setText(self.copyright)
        self.copyright_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)  # type: ignore
        self.copyright_label.setObjectName("copyright_label")  # 添加对象名称便于调试
        
        # 确保文本正确设置
        self.copyright_label.setTextFormat(Qt.TextFormat.PlainText)  # type: ignore

        self.version_label = QLabel()
        self.version_label.setText(f'Version：{self.version}')
        self.version_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)  # type: ignore
        self.version_label.setObjectName("version_label")  # 添加对象名称便于调试
        
        # 确保文本正确设置
        self.version_label.setTextFormat(Qt.TextFormat.PlainText)  # type: ignore

        # 将标签添加到信息布局中
        info_layout.addWidget(self.copyright_label)
        info_layout.addStretch()
        info_layout.addWidget(self.version_label)
        
        self.bg_layout.addLayout(info_layout)
        
        # 确保标签可见并正确调整大小
        self.copyright_label.setVisible(True)
        self.copyright_label.setWordWrap(False)  # 确保文本不换行
        self.version_label.setVisible(True)
        self.version_label.setWordWrap(False)  # 确保文本不换行
        
        # 调整标签大小以适应内容
        self.copyright_label.adjustSize()
        self.version_label.adjustSize()
        
        self.update_label.connect(self.set_text)

    def set_text(self, _str):
        self.copyright_label.setText(_str)
        # 确保文本设置后标签能正确显示
        self.copyright_label.adjustSize()
