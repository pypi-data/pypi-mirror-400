# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏

from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoSlider(QSlider):
    def __init__(self):
        super().__init__()

        self.set_style_sheet()

    def set_style_sheet(self):
        self.setStyleSheet(f"""
        /* HORIZONTAL */
        QSlider {{ 
            margin: 0px; 
        }}
        
        QSlider::groove:horizontal {{
            border-radius: 2px;
            height: 4px;
            margin: 0px;
            background-color: {THEME.bg_300};
        }}
        
        QSlider::groove:horizontal:hover {{ 
            background-color: {THEME.primary_200}; 
        }}
        
        QSlider::handle:horizontal {{
            border: none;
            height: 16px;
            width: 16px;
            margin: -6px 0;
            border-radius: 8px;
            background-color: {THEME.primary_100};
        }}
        
        QSlider::handle:horizontal:hover {{ 
            background-color: {THEME.primary_200}; 
        }}
        
        QSlider::handle:horizontal:pressed {{ 
            background-color: {THEME.primary_300}; 
        }}

        /* VERTICAL */
        QSlider::groove:vertical {{
            border-radius: 2px;
            width: 4px;
            margin: 0px;
            background-color: {THEME.bg_300};
        }}
        
        QSlider::groove:vertical:hover {{ 
            background-color: {THEME.primary_200}; 
        }}
        
        QSlider::handle:vertical {{
            border: none;
            height: 16px;
            width: 16px;
            margin: 0 -6px;
            border-radius: 8px;
            background-color: {THEME.primary_100};
        }}
        
        QSlider::handle:vertical:hover {{ 
            background-color: {THEME.primary_200}; 
        }}
        
        QSlider::handle:vertical:pressed {{ 
            background-color: {THEME.primary_300}; 
        }}
        """)