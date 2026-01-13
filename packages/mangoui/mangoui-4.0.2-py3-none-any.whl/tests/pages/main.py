# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-10-31 9:51
# @Author : 毛鹏
import asyncio
import os
import sys
from threading import Thread

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# 导入PySide6
from PySide6.QtWidgets import QApplication

# 直接从相对路径导入页面类
from home.home import HomePage
from input.input import InputPage
from display.display import DisplayPage
from container.container import ContainerPage
from layout.layout import LayoutPage
from layout.layout1 import Layout1Page
from layout.layout2 import Layout2Page
from menu.menu import MenuPage
from charts.charts import ChartsPage
from feedback.feedback import FeedbackPage
from window.window import WindowPage
from component.component_center import ComponentPage
from component.layout3 import Layout3Page
from component.layout4 import Layout4Page
from miscellaneous.miscellaneous import MiscellaneousPage

from mangoui.settings.settings import STYLE, MENUS
from mangoui.widgets.window.main_window.main_1.main_window import MangoMain1Window

os.environ["QT_FONT_DPI"] = "96"


class AsyncioThread(Thread):

    def __init__(self, loop):
        super().__init__()
        self._loop = loop
        self.daemon = True

    def run(self) -> None:
        self._loop.run_forever()


def t():
    loop = asyncio.new_event_loop()
    thd = AsyncioThread(loop)
    thd.start()
    return loop


def main():
    page_dict = {
        'home': HomePage,
        'input': InputPage,
        'display': DisplayPage,
        'container': ContainerPage,
        'layout': LayoutPage,
        'layout_page_1': Layout1Page,
        'layout_page_2': Layout2Page,
        'menu': MenuPage,
        'charts': ChartsPage,
        'feedback': FeedbackPage,
        'window': WindowPage,
        'component': ComponentPage,
        'component_page_3': Layout3Page,
        'component_page_4': Layout4Page,
        'miscellaneous': MiscellaneousPage,
    }

    app = QApplication([])
    login_window = MangoMain1Window(STYLE, MENUS, page_dict, t(), customize_titlebar=True)
    login_window.show()
    app.exec()


main()