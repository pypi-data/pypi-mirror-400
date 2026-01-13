from mangoui.models.models import AppConfig, MenusModel, Theme
from mangoui.styles.qss import *

THEME = Theme(**qss_dict_1)

STYLE = AppConfig(**{
    "app_name": "芒果pyside6组件库",
    "version": "3.5.1",
    "copyright": "Copyright © By: 芒果味  2022-2025",
    "year": 2021,
    "theme_name": "mango",
    "custom_title_bar": True,
    "lef_menu_size": {
        "minimum": 50,
        "maximum": 240
    },
    "left_menu_content_margins": 3,
    "left_column_size": {
        "minimum": 0,
        "maximum": 240
    },
    "right_column_size": {
        "minimum": 0,
        "maximum": 240
    },
})

MENUS = MenusModel(**{
    "left_menus": [
        {
            "btn_icon": ":/icons/home.svg",
            "btn_id": "home",
            "btn_text": "首页",
            "btn_tooltip": "首页",
            "show_top": True,
            "is_active": True
        },
        {
            "btn_icon": ":/icons/app_icon.svg",
            "btn_id": "input",
            "btn_text": "输入组件",
            "btn_tooltip": "输入组件",
            "show_top": True,
            "is_active": False
        },
        {
            "btn_icon": ":/icons/calendar_clock.svg",
            "btn_id": "display",
            "btn_text": "显示组件",
            "btn_tooltip": "显示组件",
            "show_top": True,
            "is_active": False
        },
        {
            "btn_icon": ":/icons/command.svg",
            "btn_id": "container",
            "btn_text": "容器组件",
            "btn_tooltip": "容器组件",
            "show_top": True,
            "is_active": False
        },
        {
            "btn_icon": ":/icons/compass.svg",
            "btn_id": "layout",
            "btn_text": "布局组件",
            "btn_tooltip": "布局组件",
            "show_top": True,
            "is_active": False,
            "submenus": [
            {
                "btn_id": "layout_page_1",
                "btn_text": "基础布局展示",
                "btn_tooltip": "基础布局展示",
                "show_top": True,
                "is_active": False
            },
            {
                "btn_id": "layout_page_2",
                "btn_text": "高级布局展示",
                "btn_tooltip": "高级布局展示",
                "show_top": True,
                "is_active": False
            },]
        },
        {
            "btn_icon": ":/icons/down.svg",
            "btn_id": "menu",
            "btn_text": "菜单组件",
            "btn_tooltip": "菜单组件",
            "show_top": True,
            "is_active": False
        },
        {
            "btn_icon": ":/icons/fill.svg",
            "btn_id": "charts",
            "btn_text": "图表组件",
            "btn_tooltip": "图表组件",
            "show_top": True,
            "is_active": False
        },
        {
            "btn_icon": ":/icons/home.svg",
            "btn_id": "feedback",
            "btn_text": "反馈组件",
            "btn_tooltip": "反馈组件",
            "show_top": True,
            "is_active": False
        },
        {
            "btn_icon": ":/icons/icon_add_user.svg",
            "btn_id": "window",
            "btn_text": "窗口组件",
            "btn_tooltip": "窗口组件",
            "show_top": True,
            "is_active": False
        },
        {
            "btn_icon": ":/icons/icon_arrow_left.svg",
            "btn_id": "component",
            "btn_text": "公共组件",
            "btn_tooltip": "公共组件",
            "show_top": True,
            "is_active": False,
            "submenus": [
            {
                "btn_id": "component_page_3",
                "btn_text": "基础公共组件展示",
                "btn_tooltip": "基础公共组件展示",
                "show_top": True,
                "is_active": False
            },
            {
                "btn_id": "component_page_4",
                "btn_text": "高级公共组件展示",
                "btn_tooltip": "高级公共组件展示",
                "show_top": True,
                "is_active": False
            },]
        },
        {
            "btn_icon": ":/icons/icon_info.svg",
            "btn_id": "miscellaneous",
            "btn_text": "其他组件",
            "btn_tooltip": "其他组件",
            "show_top": True,
            "is_active": False
        }
    ],
    "title_bar_menus": [
        {
            "btn_icon": ":/icons/project.ico",
            "btn_id": "project",
            "btn_tooltip": "请选择项目",
            "is_active": False
        }, {
            "btn_icon": ":/icons/env.ico",
            "btn_id": "test_env",
            "btn_tooltip": "请选择测试环境",
            "is_active": False
        }
    ]
})
