# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏
import os

from PySide6.QtCore import QRect, QEvent, QPoint
from PySide6.QtGui import QColor, Qt, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QLabel, QPushButton

from mangoui.settings.settings import THEME


class MangoMenuButton(QPushButton):
    def __init__(
            self,
            app_parent,
            text,
            tooltip_text='',
            url=None,
            btn_id=None,
            icon_path=None,
            is_active=False,
            height=50,
    ):
        super().__init__()
        self.setText(text)
        self.url = url
        self.setCursor(Qt.PointingHandCursor)  # type: ignore
        self.setMaximumHeight(height)
        self.setMinimumHeight(height)
        self.setObjectName(btn_id)

        self._icon_path = icon_path
        self._icon_active_menu = ":/icons/active_menu.svg"

        self._margin = 4

        self._set_icon_color = THEME.text_100
        self._set_bg_color = THEME.bg_300
        self.app_parent = app_parent
        self._is_active = is_active
        self._is_active_tab = False
        self._is_toggle_active = False
        self.tooltip_text = tooltip_text
        self.tooltip = _ToolTip(
            self.app_parent,
            self.tooltip_text,
            THEME.bg_300,
            THEME.text_200,
            THEME.text_100
        )
        self.tooltip.hide()

    def paintEvent(self, event):
        # 画家
        p = QPainter()
        # 只有在有效的 paint event 中才开始绘制
        if not p.begin(self):
            return
        p.setRenderHint(QPainter.Antialiasing)  # type: ignore
        p.setPen(Qt.NoPen)  # type: ignore
        p.setFont(self.font())

        # 矩形
        rect = QRect(4, 5, self.width(), self.height() - 10)
        rect_inside = QRect(4, 5, self.width() - 8, self.height() - 10)
        rect_icon = QRect(0, 0, 50, self.height())
        rect_blue = QRect(4, 5, 20, self.height() - 10)
        rect_inside_active = QRect(7, 5, self.width(), self.height() - 10)
        rect_text = QRect(45, 0, self.width() - 50, self.height())

        if self._is_active or self._is_active_tab:
            # 绘制BG蓝色 dark_four
            p.setBrush(QColor(THEME.accent_200))
            p.drawRoundedRect(rect_blue, 8, 8)

            # BG内部
            p.setBrush(QColor(THEME.bg_100))
            p.drawRoundedRect(rect_inside_active, 8, 8)

            # 绘制活动
            icon_path = self._icon_active_menu
            app_path = os.path.abspath(os.getcwd())
            icon_path = os.path.normpath(os.path.join(app_path, icon_path))
            self._set_icon_color = THEME.text_100
            self.icon_active(p, icon_path, self.width())

            # 绘制文本
            p.setPen(QColor(THEME.text_100))
            p.drawText(rect_text, Qt.AlignVCenter, self.text())  # type: ignore

            # 绘制图标
            self.icon_paint(p, self._icon_path, rect_icon, self._set_icon_color)

        else:
            if self._is_toggle_active:
                # BG内部
                p.setBrush(QColor(THEME.accent_200))
                p.drawRoundedRect(rect_inside, 8, 8)

                # 绘制文本
                p.setPen(QColor(THEME.bg_100))
                p.drawText(rect_text, Qt.AlignVCenter, self.text())  # type: ignore

                # 绘制图标
                if self._is_toggle_active:
                    self.icon_paint(p, self._icon_path, rect_icon, THEME.bg_300)
                else:
                    self.icon_paint(p, self._icon_path, rect_icon, self._set_icon_color)
            else:
                # BG内部
                p.setBrush(QColor(self._set_bg_color))
                p.drawRoundedRect(rect_inside, 8, 8)

                # 绘制文本
                p.setPen(QColor(THEME.text_100))
                p.drawText(rect_text, Qt.AlignVCenter, self.text())  # type: ignore

                # 绘制图标
                self.icon_paint(p, self._icon_path, rect_icon, self._set_icon_color)

        p.end()

    # 设置活动菜单
    def set_active(self, is_active):
        self._is_active = is_active
        if not is_active:
            self._set_icon_color = THEME.text_100
            self._set_bg_color = THEME.bg_300

        self.repaint()

    # 设置活动选项卡菜单
    def set_active_tab(self, is_active):
        self._is_active_tab = is_active
        if not is_active:
            self._set_icon_color = THEME.text_100
            self._set_bg_color = THEME.bg_300

        self.repaint()

    # 如果是活动菜单，则返回
    def is_active(self):
        return self._is_active

    # 如果选项卡菜单处于活动状态，则返回
    def is_active_tab(self):
        return self._is_active_tab

    # 设置活动切换
    def set_active_toggle(self, is_active):
        self._is_toggle_active = is_active

    # 设置图标
    def set_icon(self, icon_path):
        self._icon_path = icon_path
        self.repaint()

    # 用颜色绘制图标
    def icon_paint(self, qp, image, rect, color):
        if image is None:
            # 创建一个空白图像，设置大小为 rect 的大小
            icon = QPixmap(rect.size())
            icon.fill(Qt.transparent)  # type: ignore
        else:
            icon = QPixmap(image)
        if icon.isNull():
            return
        painter = QPainter(icon)
        if not painter.isActive():
            return
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)  # type: ignore
        painter.fillRect(icon.rect(), color)
        qp.drawPixmap(
            (rect.width() - icon.width()) / 2,
            (rect.height() - icon.height()) / 2,
            icon
        )
        painter.end()

    # 在右侧绘制活动图标
    def icon_active(self, qp, image, width):
        if not image:
            return
        icon = QPixmap(image)
        if icon.isNull():
            return
        painter = QPainter(icon)
        if not painter.isActive():
            return
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)  # type: ignore
        painter.fillRect(icon.rect(), THEME.bg_100)
        qp.drawPixmap(width - 5, 0, icon)
        painter.end()

    # 更改样式
    def change_style(self, event):
        if event == QEvent.Enter:  # type: ignore
            if not self._is_active:
                self._set_icon_color = THEME.text_200
                self._set_bg_color = THEME.primary_200
            self.repaint()
        elif event == QEvent.Leave:  # type: ignore
            if not self._is_active:
                self._set_icon_color = THEME.text_100
                self._set_bg_color = THEME.bg_300
            self.repaint()
        elif event == QEvent.MouseButtonPress:  # type: ignore
            if not self._is_active:
                self._set_icon_color = THEME.text_100
                self._set_bg_color = THEME.primary_300
            self.repaint()
        elif event == QEvent.MouseButtonRelease:  # type: ignore
            if not self._is_active:
                self._set_icon_color = THEME.text_100
                self._set_bg_color = THEME.bg_300
            self.repaint()

    # 当鼠标位于BTN上时触发的事件
    def enterEvent(self, event):
        self.change_style(QEvent.Enter)  # type: ignore
        if self.width() == 50 and self.tooltip_text:
            self.move_tooltip()
            self.tooltip.show()

    # 鼠标离开BTN时触发的事件
    def leaveEvent(self, event):
        self.change_style(QEvent.Leave)  # type: ignore
        self.tooltip.hide()

    # 按下左键时触发的事件
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # type: ignore
            self.change_style(QEvent.MouseButtonPress)  # type: ignore
            self.tooltip.hide()
            return self.clicked.emit()

    # 松开鼠标按钮后触发的事件
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:  # type: ignore
            self.change_style(QEvent.MouseButtonRelease)  # type: ignore
            return self.released.emit()

    def move_tooltip(self):
        gp = self.mapToGlobal(QPoint(0, 0))

        pos = self.app_parent.mapFromGlobal(gp)

        pos_x = pos.x() + self.width() + 5
        pos_y = pos.y() + (self.width() - self.tooltip.height()) // 2

        self.tooltip.move(pos_x, pos_y)


class _ToolTip(QLabel):
    def __init__(
            self,
            parent,
            tooltip,
            dark_one,
            context_color,
            text_foreground
    ):
        QLabel.__init__(self)
        
        style = f"""QLabel {{ background-color: {dark_one}; color: {text_foreground}; padding: 6px 12px; border-radius: {THEME.border_radius}; border: 1px solid {context_color}; font-family: {THEME.font.family}; font-size: {THEME.font.text_size}px; font-weight: 500; }}"""
        self.setObjectName(u"label_tooltip")
        self.setStyleSheet(style)
        self.setMinimumHeight(34)
        self.setParent(parent)
        self.setText(tooltip)
        self.adjustSize()

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)