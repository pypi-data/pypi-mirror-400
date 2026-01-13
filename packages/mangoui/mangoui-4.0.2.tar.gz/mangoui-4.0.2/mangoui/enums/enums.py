# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-10-08 16:25
# @Author : 毛鹏
from enum import Enum


class InputEnum(Enum):
    INPUT = 0
    SELECT = 1
    CASCADER = 2
    TOGGLE = 3
    SELECT_MANY = 4
    TEXT = 5


class TableTypeEnum(Enum):
    DEFAULT = 0
    MENU = 1
    LABEL = 2
    TOGGLE = 3


class StatusEnum(Enum):
    """状态枚举"""
    SUCCESS = 1
    FAIL = 0

    @classmethod
    def obj(cls):
        return {0: "关闭&进行中&失败", 1: "启用&已完成&通过"}


class Status1Enum(Enum):
    """状态枚举"""
    SUCCESS = 1
    FAIL = 0

    @classmethod
    def obj(cls):
        return {0: "否", 1: "是"}
