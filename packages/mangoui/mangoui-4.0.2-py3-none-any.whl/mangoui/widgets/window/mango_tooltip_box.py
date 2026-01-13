# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-05-27 13:04
# @Author : 毛鹏
from PySide6.QtWidgets import QMessageBox

from mangoui.settings.settings import THEME


def show_failed_message(text: str, title: str = '失败'):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)  # type: ignore
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.setStyleSheet(f"""
        QMessageBox {{
            background-color: {THEME.bg_100};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}
        QPushButton {{
            background-color: {THEME.primary_100};
            color: white;
            border-radius: {THEME.border_radius};
            padding: 5px 15px;
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}
        QPushButton:hover {{
            background-color: {THEME.primary_200};
        }}
    """)
    msg.exec()


def show_success_message(text: str, title: str = '成功'):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)  # type: ignore
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStyleSheet(f"""
        QMessageBox {{
            background-color: {THEME.bg_100};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}
        QPushButton {{
            background-color: {THEME.primary_100};
            color: white;
            border-radius: {THEME.border_radius};
            padding: 5px 15px;
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}
        QPushButton:hover {{
            background-color: {THEME.primary_200};
        }}
    """)
    msg.exec()


def show_warning_message(text: str, title: str = '警告'):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)  # type: ignore
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.setStyleSheet(f"""
        QMessageBox {{
            background-color: {THEME.bg_100};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}
        QPushButton {{
            background-color: {THEME.primary_100};
            color: white;
            border-radius: {THEME.border_radius};
            padding: 5px 15px;
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}
        QPushButton:hover {{
            background-color: {THEME.primary_200};
        }}
    """)
    msg.exec()


def show_info_message(text: str, title: str = '提示'):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)  # type: ignore
    msg.setText(text)
    msg.setWindowTitle(title)
    msg.setStyleSheet(f"""
        QMessageBox {{
            background-color: {THEME.bg_100};
            color: {THEME.text_100};
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}
        QPushButton {{
            background-color: {THEME.primary_100};
            color: white;
            border-radius: {THEME.border_radius};
            padding: 5px 15px;
            font-family: {THEME.font.family};
            font-size: {THEME.font.text_size}px;
        }}
        QPushButton:hover {{
            background-color: {THEME.primary_200};
        }}
    """)
    msg.exec()