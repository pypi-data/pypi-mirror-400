# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-10-08 16:15
# @Author : 毛鹏
from typing import Any

from pydantic import BaseModel

from mangoui.enums.enums import InputEnum, TableTypeEnum


class Font(BaseModel):
    family: str
    title_size: int
    text_size: int
    weight: str


class GroupColors(BaseModel):
    info: str
    warning: str
    success: str
    error: str


class State(BaseModel):
    background_color: str
    color: str


class Theme(BaseModel):
    theme_name: str
    # 主题色
    primary_000: str    # 主色
    primary_100: str    # 主色
    primary_200: str    # 主色（浅）
    primary_300: str    # 主色（最浅）
    accent_100: str     # 强调色
    accent_200: str     # 强调色（深）
    text_100: str       # 主要文本颜色
    text_200: str       # 次要文本颜色
    bg_100: str         # 背景色
    bg_200: str         # 次要背景色
    bg_300: str         # 较深背景色
    # 边距和边距颜色
    border: str
    border_radius: str
    # 字体
    font: Font
    # 其他颜色组，如通知、警告、成功、错误等
    group: GroupColors


class LeftMenuSize(BaseModel):
    minimum: int
    maximum: int


class ColumnSize(BaseModel):
    minimum: int
    maximum: int


class AppConfig(BaseModel):
    app_name: str
    version: str
    copyright: str
    year: int
    theme_name: str
    custom_title_bar: bool

    lef_menu_size: LeftMenuSize
    left_menu_content_margins: int
    left_column_size: ColumnSize
    right_column_size: ColumnSize


class ThemeConfig(BaseModel):
    theme_name: str
    dark_one: str
    dark_two: str
    dark_three: str
    dark_four: str
    bg_one: str
    bg_two: str
    bg_three: str
    icon_color: str
    icon_hover: str
    icon_pressed: str
    icon_active: str
    context_color: str
    context_hover: str
    context_pressed: str
    text_title: str
    text_foreground: str
    text_description: str
    text_active: str
    white: str
    pink: str
    green: str
    red: str
    yellow: str
    blue: str
    orange: str
    radius: str
    border_size: str
    font: Font


class LeftMenuModel(BaseModel):
    btn_icon: str | None = None
    btn_id: str
    btn_text: str
    btn_tooltip: str
    show_top: bool
    is_active: bool
    is_active: bool
    submenus: list['LeftMenuModel'] = []
    url: str | None = None
    but_obj: Any | None = None
    frame_object: Any | None = None


class TitleBarMenusModel(BaseModel):
    btn_icon: str
    btn_id: str
    btn_tooltip: str
    is_active: bool


class MenusModel(BaseModel):
    left_menus: list[LeftMenuModel]
    title_bar_menus: list[TitleBarMenusModel]


class SearchDataModel(BaseModel):
    title: str
    placeholder: str
    key: str
    type: InputEnum = InputEnum.INPUT
    select: dict | list[dict] | Any = None
    input_object: None = None
    value: str | None = None
    subordinate: str | None = None  # 是否联动下级选择条件


class RightDataModel(BaseModel):
    name: str
    theme: str
    action: str
    obj: Any | None = None


class FormDataModel(BaseModel):
    title: str
    placeholder: str
    key: str
    input_object: None = None
    value: str | None = None
    type: InputEnum = InputEnum.INPUT
    select: dict | list[dict] | Any = None  # 选项数据
    subordinate: str | None = None  # 是否联动下级选择条件
    required: bool = True  # 是否必填


class TableColumnModel(BaseModel):
    key: str
    name: str
    width: int | None = None
    type: TableTypeEnum = 0
    option: dict | list[dict] | None = None


class TableMenuItemModel(BaseModel):
    name: str
    action: str
    son: list['TableMenuItemModel'] = []


class FieldListModel(BaseModel):
    key: str
    name: str


class CascaderModel(BaseModel):
    value: str
    label: str
    parameter: dict | None = None
    children: list['CascaderModel'] = []

    @classmethod
    def get_model(cls, data):
        if isinstance(data, dict):
            data = [data]
        return [
            cls(
                value=str(i['value']),
                label=i['label'],
                parameter=i.get('parameter'),
                children=cls.get_model(i.get('children', []))
            ) for i in data
        ]


class TreeModel(BaseModel):
    key: str
    status: int
    title: str
    children: list['TreeModel'] = []
    data: Any | None = None

    @classmethod
    def get_model(cls, data):
        return [cls(
            key=str(i['key']),
            status=i['status'],
            title=i.get('title'),
            data=i,
            children=[cls.get_model(child) for child in i.get('children', [])]) for i in data]


class DialogCallbackModel(BaseModel):
    key: str | None = None
    value: int | str | None
    input_object: Any | None = None
    subordinate: str
    subordinate_input_object: Any | None = None


class ComboBoxDataModel(BaseModel):
    id: str | None
    name: str | None

    @classmethod
    def get_model(cls, data):
        return [cls(id=str(i['id']), name=i['name']) for i in data]
