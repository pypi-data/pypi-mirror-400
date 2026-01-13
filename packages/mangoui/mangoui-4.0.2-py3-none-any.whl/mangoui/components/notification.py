# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-04 14:36
# @Author : 毛鹏
from PySide6.QtCore import QPoint

from mangoui.settings.settings import THEME
from mangoui.widgets.display import MangoNotification


def success_notification(parent, text):
    notification = MangoNotification(parent, text, THEME.group.success)
    # 获取主窗口右上角位置
    parent_pos = parent.mapToGlobal(QPoint(parent.width() - notification.width() - 10, 40))
    notification.move(parent_pos)
    notification.show()


def info_notification(parent, text):
    notification = MangoNotification(parent, text, THEME.group.info)
    # 获取主窗口右上角位置
    parent_pos = parent.mapToGlobal(QPoint(parent.width() - notification.width() - 10, 50))
    notification.move(parent_pos)
    notification.show()


def warning_notification(parent, text):
    notification = MangoNotification(parent, text, THEME.group.warning)
    # 获取主窗口右上角位置
    parent_pos = parent.mapToGlobal(QPoint(parent.width() - notification.width() - 10, 60))
    notification.move(parent_pos)
    notification.show()


def error_notification(parent, text):
    notification = MangoNotification(parent, text, THEME.group.error)
    # 获取主窗口右上角位置
    parent_pos = parent.mapToGlobal(QPoint(parent.width() - notification.width() - 10, 20))
    notification.move(parent_pos)
    notification.show()
