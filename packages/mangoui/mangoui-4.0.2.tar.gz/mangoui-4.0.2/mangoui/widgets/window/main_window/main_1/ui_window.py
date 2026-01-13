# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏
import webbrowser

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.models.models import MenusModel, AppConfig, LeftMenuModel
from mangoui.settings.settings import THEME
from mangoui.widgets.menu import MangoMenu
from mangoui.widgets.miscellaneous.mango_credits import MangoCredits
from mangoui.widgets.miscellaneous.mango_grips import MangoGrips
from mangoui.widgets.title_bar.mango_title_bar import MangoTitleBar
from mangoui.widgets.window.main_window.main_1.pages_window import PagesWindow
from mangoui.widgets.window.mango_frame import MangoFrame


class UIWindow(QMainWindow):
    clicked = Signal(object)

    def __init__(self, style: AppConfig, menus: MenusModel, page_dict, l=None, **kwargs):
        super().__init__()
        self.style = style
        self.menus = menus
        self.loop = l
        self.page_dict = page_dict
        self.kwargs = kwargs
        self.page = None
        self.setWindowTitle(self.style.app_name)
        screen = QGuiApplication.primaryScreen().geometry()
        if kwargs.get('width_coefficient'):
            width = int(screen.width() * kwargs.get('width_coefficient'))
        else:
            width = int(screen.width() * 0.6)
        if kwargs.get('height_coefficient'):
            height = int(screen.height() * kwargs.get('height_coefficient'))
        else:
            height = int(screen.height() * 0.7)
        self.resize(width, height)
        self.setMinimumSize(int(width * 0.8), int(height * 0.8))

        self.central_widget = QWidget()
        self.central_widget.setStyleSheet(f'''
            font: {THEME.font.text_size}pt "{THEME.font.family}";
            color: {THEME.text_100};
        ''')
        self.central_widget_layout = QVBoxLayout(self.central_widget)
        if self.style.custom_title_bar:
            self.central_widget_layout.setContentsMargins(10, 10, 10, 10)
        else:
            self.central_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.central_widget)

        self.window = MangoFrame(self)
        if not self.style.custom_title_bar:
            self.window.set_stylesheet(border_radius=0, border_size=0)
        self.central_widget_layout.addWidget(self.window)

        self.menus_ui()
        self.right_app_frame = QFrame()
        self.right_app_layout = QVBoxLayout(self.right_app_frame)
        self.right_app_layout.setContentsMargins(3, 3, 3, 3)
        self.right_app_layout.setSpacing(6)
        self.window.layout.addWidget(self.right_app_frame)
        self.title_bar_ui()
        self.content_ui()
        self.bottom_ui()

    def menus_ui(self):
        self.left_menu_frame = QFrame()
        self.left_menu_frame.setMaximumSize(
            self.style.lef_menu_size.minimum + (self.style.left_menu_content_margins * 2), 17280)
        self.left_menu_frame.setMinimumSize(
            self.style.lef_menu_size.minimum + (self.style.left_menu_content_margins * 2), 0)
        self.left_menu_layout = QHBoxLayout(self.left_menu_frame)
        self.left_menu_layout.setContentsMargins(3, 3, 3, 3)
        self.left_menu = MangoMenu(
            parent=self.left_menu_frame,
            app_parent=self.central_widget,
        )
        self.left_menu.add_menus(self.menus.left_menus)
        self.left_menu.clicked.connect(self.btn_clicked)
        self.left_menu.released.connect(self.btn_released)
        self.left_menu_layout.addWidget(self.left_menu)
        self.window.layout.addWidget(self.left_menu_frame)

    def title_bar_ui(self):
        self.title_bar_frame = QFrame()
        self.title_bar_frame.setMinimumHeight(40)
        self.title_bar_frame.setMaximumHeight(40)
        self.title_bar_layout = QVBoxLayout(self.title_bar_frame)
        self.title_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = MangoTitleBar(self, self.central_widget,
                                       customize_titlebar=self.kwargs.get('customize_titlebar', False))
        self.title_bar.add_menus(self.menus.title_bar_menus)
        self.title_bar.clicked.connect(self.title_ber_but_clicked)
        self.title_bar.released.connect(self.btn_released)

        self.title_bar_layout.addWidget(self.title_bar)
        self.right_app_layout.addWidget(self.title_bar_frame)

        if self.style.custom_title_bar:
            self.title_bar.set_title(self.style.app_name)
            self.setWindowFlag(Qt.FramelessWindowHint)  # type: ignore
            self.setAttribute(Qt.WA_TranslucentBackground)  # type: ignore
            self.left_grip = MangoGrips(self, "left", )
            self.right_grip = MangoGrips(self, "right", )
            self.top_grip = MangoGrips(self, "top", )
            self.bottom_grip = MangoGrips(self, "bottom", )
            self.top_left_grip = MangoGrips(self, "top_left", )
            self.top_right_grip = MangoGrips(self, "top_right", )
            self.bottom_left_grip = MangoGrips(self, "bottom_left", )
            self.bottom_right_grip = MangoGrips(self, "bottom_right", )

    def content_ui(self):
        self.content_area_frame = QFrame()
        self.content_area_layout = QHBoxLayout(self.content_area_frame)
        self.content_area_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area_layout.setSpacing(0)

        self.content_area_left_frame = QFrame()
        self.content_area_left_frame.setObjectName("contentAreaLeftFrame")
        self.content_area_left_frame.setStyleSheet("""
            QFrame#contentAreaLeftFrame {
                background-color: #ffffff;
                border: none;
            }
        """)

        self.load_pages = PagesWindow(self, self.content_area_left_frame, self.page_dict)

        self.load_pages.set_page(self.kwargs.get('page') if self.kwargs.get('page') else 'home')
        self.content_area_layout.addWidget(self.content_area_left_frame)
        self.right_app_layout.addWidget(self.content_area_frame)
        self.right_app_layout.setStretch(1, 1)  # 让内容区域占据剩余空间

    def bottom_ui(self):
        self.credits_frame = QFrame()
        self.credits_frame.setMinimumHeight(28)
        self.credits_frame.setMaximumHeight(28)
        self.credits_layout = QVBoxLayout(self.credits_frame)
        self.credits_layout.setContentsMargins(0, 0, 0, 0)
        self.credits = MangoCredits(self.style.copyright, self.style.version)
        self.credits_layout.addWidget(self.credits)
        self.right_app_layout.addWidget(self.credits_frame)

    def btn_released(self):
        btn = self.__setup_btn()

    @staticmethod
    def animate_frame(parent, frame, duration=300):
        """
        从上往下展开 QFrame 的动画效果。

        :param frame: 要显示的 QFrame
        :param duration: 动画持续时间（毫秒）
        """
        animation = QPropertyAnimation(frame, b"minimumWidth")
        animation.stop()
        # 先显示 frame 以获取正确的宽度
        frame.show()
        # 强制更新布局以获取正确的尺寸
        frame.updateGeometry()
        QApplication.processEvents()
        current_width = frame.width()
        # 如果宽度为0，使用一个合理的默认值
        if current_width == 0:
            current_width = 200  # 默认宽度
        # 设置动画的起始值和结束值
        animation.setStartValue(0)
        animation.setEndValue(current_width)
        animation.setEasingCurve(QEasingCurve.InOutCubic)
        animation.setDuration(duration)
        animation.start()

    def title_ber_but_clicked(self):
        btn = self.__setup_btn()
        if btn.url:
            webbrowser.open(btn.url)
            return
        btn_name = btn.objectName()
        self.clicked.emit(btn_name)

    def btn_clicked(self, menu_obj: LeftMenuModel):
        if menu_obj.url:
            webbrowser.open(menu_obj.url)
            return
        for i in self.left_menu.menu_model:
            if i.btn_id != menu_obj.btn_id and i.frame_object and menu_obj.btn_id not in [e.btn_id for e in i.submenus]:
                i.frame_object.hide()

        if menu_obj.frame_object:
            if menu_obj.frame_object.isHidden():
                self.left_menu.toggle_animation(False)
                self.animate_frame(self.left_menu.parent, menu_obj.frame_object)
            else:
                menu_obj.frame_object.hide()
        else:
            self.left_menu.select_only_one(menu_obj.btn_id)
            self.load_pages.set_page(menu_obj.btn_id)

    def get_title_bar_btn(self, object_name):
        return self.title_bar_frame.findChild(QPushButton, object_name)

    def __setup_btn(self):
        if self.title_bar.sender() is not None:
            return self.title_bar.sender()
        elif self.left_menu.sender() is not None:
            return self.left_menu.sender()

    def resize_grips(self):
        if self.style.custom_title_bar:
            self.left_grip.setGeometry(5, 10, 10, self.height())
            self.right_grip.setGeometry(self.width() - 15, 10, 10, self.height())
            self.top_grip.setGeometry(5, 5, self.width() - 10, 10)
            self.bottom_grip.setGeometry(5, self.height() - 15, self.width() - 10, 10)
            self.top_left_grip.setGeometry(self.width() - 20, 5, 15, 15)
            self.top_right_grip.setGeometry(self.width() - 20, 5, 15, 15)
            self.bottom_left_grip.setGeometry(5, self.height() - 20, 15, 15)
            self.bottom_right_grip.setGeometry(self.width() - 20, self.height() - 20, 15, 15)

    def set_page(self, page: str, data: dict | None = None):
        self.load_pages.set_page(page, data)
