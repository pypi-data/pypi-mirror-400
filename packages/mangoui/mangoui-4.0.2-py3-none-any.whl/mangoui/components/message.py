# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-04 14:35
# @Author : 毛鹏
from PySide6.QtCore import QPoint

from mangoui.settings.settings import THEME
from mangoui.widgets.display import MangoMessage


def info_message(parent, text):
    message = MangoMessage(parent, text, THEME.group.info)
    parent_pos = parent.mapToGlobal(QPoint(parent.width() // 2 - message.width() // 2, 0))
    message.move(parent_pos)
    message.show()


def success_message(parent, text):
    message = MangoMessage(parent, text, THEME.group.success)
    parent_pos = parent.mapToGlobal(QPoint(parent.width() // 2 - message.width() // 2, 0))
    message.move(parent_pos)
    message.show()


def warning_message(parent, text):
    message = MangoMessage(parent, text, THEME.group.warning)
    parent_pos = parent.mapToGlobal(QPoint(parent.width() // 2 - message.width() // 2, 0))
    message.move(parent_pos)
    message.show()


def error_message(parent, text):
    message = MangoMessage(parent, text, THEME.group.error)
    parent_pos = parent.mapToGlobal(QPoint(parent.width() // 2 - message.width() // 2, 0))
    message.move(parent_pos)
    message.show()
