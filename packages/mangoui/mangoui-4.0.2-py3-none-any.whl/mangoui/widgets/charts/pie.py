# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-10-23 17:49
# @Author : 毛鹏
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PySide6.QtGui import QPainterPath, QRegion
from PySide6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from mangoui.settings.settings import THEME


class RoundedCanvas(FigureCanvasQTAgg):
    def __init__(self, fig, parent=None):
        super().__init__(fig)
        self.setParent(parent)
        self.radius = 8

    def paintEvent(self, event):
        # 创建圆角路径
        path = QPainterPath()
        rect = self.rect()
        path.addRoundedRect(rect, self.radius, self.radius)

        # 设置裁剪区域
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

        # 调用父类绘制
        super().paintEvent(event)


matplotlib.rcParams['font.family'] = 'SimHei'
matplotlib.rcParams['axes.unicode_minus'] = False


class MangoPiePlot(QWidget):
    def __init__(self):
        super().__init__()
        # 设置卡片样式
        self.setStyleSheet(f"""
            background: {THEME.bg_100};
            border-radius: {THEME.border_radius};
            border: 1px solid {THEME.bg_300};
            padding: 16px;
        """)

        # 创建图表
        self.fig, self.ax = plt.subplots()
        self.fig.patch.set_facecolor('none')  # 透明背景
        self.canvas = RoundedCanvas(self.fig, self)
        
        # 设置图表标题样式
        self.ax.title.set_color(THEME.text_100)
        self.ax.title.set_fontsize(THEME.font.title_size)
        self.ax.title.set_fontfamily(THEME.font.family)

        # 布局设置
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def draw(self, data: list[dict]):
        self.ax.clear()  # 清除之前的图
        sizes = [item['value'] for item in data]
        labels = [item['name'] for item in data]
        # 使用更美观的颜色方案
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                  '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                  '#bcbd22', '#17becf']
        if all(size == 0 for size in sizes):
            # 绘制默认饼状图
            default_sizes = [1, 1]  # 两个部分，表示无数据
            default_labels = ['无数据', '']
            # 无数据样式
            self.ax.pie(
                default_sizes,
                labels=default_labels,
                colors=['#CCCCCC', '#FFFFFF'],
                startangle=90,
                textprops={'color': THEME.text_200, 'fontsize': THEME.font.text_size}
            )
        else:
            # 绘制饼图
            # 绘制饼图
            self.ax.pie(
                sizes,
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'color': THEME.text_100, 'fontsize': THEME.font.text_size},
                wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
            )
        self.ax.axis('equal')  # 确保饼状图是圆形
        self.canvas.draw()
