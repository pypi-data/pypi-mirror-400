# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-08-16 17:05
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from mangoui.settings.settings import THEME


class MangoIconButton(QPushButton):
    def __init__(
            self,
            parent,
            app_parent,
            icon_path=":/icons/icon_heart.svg",
            tooltip_text="",
            btn_id=None
    ):
        super().__init__()
        self.parent = parent
        self.setObjectName(btn_id)
        self.app_parent = app_parent
        self.tooltip_text = tooltip_text

        self.setFixedSize(30, 30)
        self.setCursor(Qt.PointingHandCursor)  # type: ignore

        self._context_color = "#568af2"
        self.text_foreground = "#8a95aa"
        self._set_bg_color = THEME.bg_100

        self._top_margin = 40
        self._is_active = False
        self._set_icon_path = icon_path
        self._set_icon_color = THEME.primary_100

        self.tooltip = _ToolTip(
            app_parent,
            tooltip_text,
            THEME.bg_300,
            self.text_foreground
        )
        self.tooltip.hide()

    def set_active(self, is_active):
        self._is_active = is_active
        self.repaint()

    def is_active(self):
        return self._is_active

    def paintEvent(self, event):
        paint = QPainter()
        if not paint.begin(self):
            return
        paint.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._is_active:
            brush = QBrush(QColor(self._context_color))
        else:
            brush = QBrush(QColor(self._set_bg_color))

        rect = QRect(0, 0, self.width(), self.height())
        paint.setPen(Qt.NoPen)  # type: ignore
        paint.setBrush(brush)
        paint.drawRoundedRect(
            rect,
            THEME.border_radius,
            THEME.border_radius
        )

        self.icon_paint(paint, self._set_icon_path, rect)

        paint.end()

    def change_style(self, event):
        if event == QEvent.Enter:  # type: ignore
            self._set_bg_color = THEME.primary_200
            self._set_icon_color = THEME.icon_hover
            self.repaint()
        elif event == QEvent.Leave:  # type: ignore
            self._set_bg_color = THEME.bg_300
            self._set_icon_color = THEME.primary_100
            self.repaint()
        elif event == QEvent.MouseButtonPress:  # type: ignore
            self._set_bg_color = THEME.primary_300
            self._set_icon_color = THEME.primary_100
            self.repaint()
        elif event == QEvent.MouseButtonRelease:  # type: ignore
            self._set_bg_color = THEME.bg_300
            self._set_icon_color = THEME.icon_hover
            self.repaint()

    def enterEvent(self, event):
        self.change_style(QEvent.Enter)  # type: ignore
        self.move_tooltip()
        self.tooltip.show()

    def leaveEvent(self, event):
        self.change_style(QEvent.Leave)  # type: ignore
        self.move_tooltip()
        self.tooltip.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # type: ignore
            self.change_style(QEvent.MouseButtonPress)  # type: ignore
            self.setFocus()
            return self.clicked.emit()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:  # type: ignore
            self.change_style(QEvent.MouseButtonRelease)  # type: ignore
            return self.released.emit()

    def icon_paint(self, qp, image, rect):
        if not image:
            return
        icon = QPixmap(image)
        if icon.isNull():
            return
        painter = QPainter(icon)
        if not painter.isActive():
            return
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)  # type: ignore
        if self._is_active:
            painter.fillRect(icon.rect(), THEME.primary_100)
        else:
            painter.fillRect(icon.rect(), self._set_icon_color)
        qp.drawPixmap(
            (rect.width() - icon.width()) / 2,
            (rect.height() - icon.height()) / 2,
            icon
        )
        painter.end()

    def set_icon(self, icon_path):
        self._set_icon_path = icon_path
        self.repaint()

    def move_tooltip(self):
        gp = self.mapToGlobal(QPoint(0, 0))

        pos = self.parent.mapFromGlobal(gp)

        pos_x = (pos.x() - (self.tooltip.width() // 2)) + (self.width() // 2)
        pos_y = pos.y() - self._top_margin

        self.tooltip.move(pos_x, pos_y)


class _ToolTip(QLabel):
    style_tooltip = """ 
    QLabel {{		
        background-color: {_dark_one};	
        color: {_text_foreground};
        padding-left: 10px;
        padding-right: 10px;
        border-radius: 17px;
        border: 0px solid transparent;
        font: 800 9pt "Segoe UI";
    }}
    """

    def __init__(
            self,
            parent,
            tooltip,
            dark_one,
            text_foreground
    ):
        QLabel.__init__(self)

        style = self.style_tooltip.format(
            _dark_one=dark_one,
            _text_foreground=text_foreground
        )
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
