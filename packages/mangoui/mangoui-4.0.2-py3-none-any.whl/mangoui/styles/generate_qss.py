# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-01-28 16:03
# @Author : 毛鹏
from PySide6.QtWidgets import QApplication


def generate_qss(theme):
    return """
        /* ==========================================
           全新现代化样式系统 v2.0
           设计理念：优雅、现代、直观
        ========================================== */
        
        /* 全局样式重置和基础样式 */
        * {
            box-sizing: border-box;
        }
        
        /* 主窗口样式 */
        QMainWindow {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 %(neutral_50)s, stop: 1 %(neutral_100)s);
            font-family: %(font_family)s;
            color: %(text_100)s;
            font-size: %(font_size_base)s;
        }
        
        /* 图表组件样式 */
        MangoLinePlot#mango_line_plot {
            background: %(bg_100)s;
            border-radius: %(radius_lg)s;
            padding: %(spacing_3)s;
            border: %(border)s;
        }
        
        MangoPiePlot#mango_pie_plot {
            background: %(bg_100)s;
            border-radius: %(radius_lg)s;
            padding: %(spacing_3)s;
            border: %(border)s;
        }

        /* 卡片组件样式 */
        MangoCard#mango_card {
            background-color: %(bg_100)s;
            border: %(border)s;
            border-radius: %(radius_xl)s;
            padding: %(spacing_4)s;
        }
        
        MangoCard#mango_card > QFrame {
            background-color: %(bg_100)s;
            border: %(border)s;
            border-radius: %(radius_xl)s;
            padding: %(spacing_4)s;
        }
        
        /* 标签组件样式 */
        MangoLabel#mango_label {
            background-color: transparent;
            color: %(text_100)s;
            font-family: %(font_family)s;
            font-size: %(font_size_base)s;
        }

        /* 表格组件样式 */
        MangoTable#mango_table {
            background-color: %(bg_100)s;
            padding: %(spacing_0)s;
            border-radius: %(radius_lg)s;
            color: %(text_100)s;
            border: %(border)s;
            alternate-background-color: %(bg_200)s;
            selection-background-color: %(primary_500)s;
            selection-color: white;
            gridline-color: %(bg_300)s;
        }
        
        MangoTable#mango_table::item {
            border: none;
            padding: %(spacing_2)s %(spacing_3)s;
            border-bottom: %(border)s;
        }
        
        MangoTable#mango_table::item:selected {
            background-color: %(primary_500)s;
            color: white;
        }

        MangoTable#mango_table QHeaderView::section {
            background-color: %(bg_200)s;
            border: none;
            border-bottom: 1px solid %(bg_300)s;
            padding: %(spacing_2)s %(spacing_3)s;
            font-weight: %(font_weight_semibold)s;
            color: %(text_100)s;
            font-size: %(font_size_sm)s;
        }
        
        MangoTable#mango_table QHeaderView::section:hover {
            background-color: %(bg_300)s;
        }
        
        MangoTable#mango_table::horizontalHeader {
            background-color: %(bg_200)s;
        }
        
        MangoTable#mango_table QTableCornerButton::section {
            border: none;
            background-color: %(bg_200)s;
            border-top-left-radius: %(radius_lg)s;
        }
        
        MangoTable#mango_table QHeaderView::section:horizontal {
            border: none;
            background-color: %(bg_200)s;
            padding: %(spacing_2)s %(spacing_3)s;
        }
        
        MangoTable#mango_table QHeaderView::section:vertical {
            border: none;
            background-color: %(bg_200)s;
            padding: %(spacing_2)s %(spacing_3)s;
            border-bottom: %(border)s;
        }

        /* 滚动条样式 */
        QScrollBar:horizontal {
            border: none;
            background: %(bg_100)s;
            height: 10px;
            margin: 0px 21px 0 21px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:horizontal {
            background: %(bg_300)s;
            min-width: 25px;
            border-radius: 5px;
        }
        
        QScrollBar::add-line:horizontal {
            border: none;
            background: %(bg_300)s;
            width: 20px;
            border-top-right-radius: 5px;
            border-bottom-right-radius: 5px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }
        
        QScrollBar::sub-line:horizontal {
            border: none;
            background: %(bg_300)s;
            width: 20px;
            border-top-left-radius: 5px;
            border-bottom-left-radius: 5px;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }
        
        QScrollBar::up-arrow:horizontal, QScrollBar::down-arrow:horizontal {
            background: none;
        }
        
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }

        QScrollBar:vertical {
            border: none;
            background: %(bg_100)s;
            width: 10px;
            margin: 21px 0 21px 0;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical {
            background: %(bg_300)s;
            min-height: 25px;
            border-radius: 5px;
        }
        
        QScrollBar::add-line:vertical {
            border: none;
            background: %(bg_300)s;
            height: 20px;
            border-bottom-left-radius: 5px;
            border-bottom-right-radius: 5px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }
        
        QScrollBar::sub-line:vertical {
            border: none;
            background: %(bg_300)s;
            height: 20px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            background: none;
        }
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        
        /* 时间编辑器样式 */
        MangoTimeEdit#mango_time_edit {
            background-color: %(bg_100)s;
            border-radius: %(radius)s;
            border: %(border)s;
            padding: %(spacing_2)s %(spacing_3)s;
            selection-color: white;
            selection-background-color: %(primary_500)s;
            color: %(text_100)s;
            font-family: %(font_family)s;
            font-size: %(font_size_base)s;
        }
        
        MangoTimeEdit#mango_time_edit:focus {
            border: 1px solid %(primary_500)s;
            background-color: %(bg_100)s;
        }
        
        MangoTimeEdit::up-button, MangoTimeEdit::down-button {
            border: none;
            background: transparent;
            width: 0;
            height: 0;
            margin: 0;
            padding: 0;
        }
        
        /* 级联选择器样式 */
        MangoCascade#mango_cascade {
            background-color: %(bg_100)s;
            border-radius: %(radius_full)s;
            border: %(border)s;
            padding: %(spacing_2)s %(spacing_4)s;
            color: %(text_100)s;
            font-family: %(font_family)s;
            font-size: %(font_size_base)s;
            font-weight: %(font_weight_semibold)s;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        MangoCascade#mango_cascade:focus {
            border: 1px solid %(primary_500)s;
            background-color: %(bg_100)s;
        }

        MangoCascade#mango_cascade::menu-indicator {
            image: url(:/icons/down.svg);
        }
        
        MangoCascade#mango_cascade QMenu {
            background-color: %(bg_100)s;
            border: %(border)s;
            border-radius: %(radius_lg)s;
            padding: %(spacing_1)s;
        }

        MangoCascade#mango_cascade QMenu::item {
            padding: %(spacing_2)s %(spacing_3)s;
            color: %(text_100)s;
            border-radius: %(radius_sm)s;
        }

        MangoCascade#mango_cascade QMenu::item:selected {
            background-color: %(primary_100)s;
            color: %(text_100)s;
        }
        
        /* 组合框样式 */
        MangoComboBoxMany#mango_combo_box_many {
            background-color: %(bg_100)s;
            border-radius: %(radius)s;
            border: %(border)s;
            padding: %(spacing_2)s %(spacing_3)s;
            selection-color: white;
            selection-background-color: %(primary_500)s;
            color: %(text_100)s;
            font-family: %(font_family)s;
            font-size: %(font_size_base)s;
        }
        
        MangoComboBoxMany#mango_combo_box_many:focus {
            border: 1px solid %(primary_500)s;
            background-color: %(bg_100)s;
        }
        
        MangoComboBoxMany#mango_combo_box_many::drop-down {
            border: none;
            background-color: transparent;
            background-image: url(:/icons/down.svg);
            background-repeat: no-repeat;
            background-position: center;
            width: 20px;
        }
        
        MangoComboBox#mango_combo_box {
            background-color: %(bg_100)s;
            border-radius: %(radius)s;
            border: %(border)s;
            padding: %(spacing_2)s %(spacing_3)s;
            selection-color: white;
            selection-background-color: %(primary_500)s;
            color: %(text_100)s;
            font-family: %(font_family)s;
            font-size: %(font_size_base)s;
        }
        
        MangoComboBox#mango_combo_box:focus {
            border: 1px solid %(primary_500)s;
            background-color: %(bg_100)s;
        }
        
        MangoComboBox#mango_combo_box::drop-down {
            border: none;
            background-color: transparent;
            background-image: url(:/icons/down.svg);
            background-repeat: no-repeat;
            background-position: center;
            width: 20px;
        }
        
        /* 文本输入框样式 */
        MangoLineEdit#mango_line_edit {
            background-color: %(bg_100)s;
            border-radius: %(radius)s;
            border: %(border)s;
            padding: %(spacing_2)s %(spacing_3)s;
            selection-color: white;
            selection-background-color: %(primary_500)s;
            color: %(text_100)s;
            font-family: %(font_family)s;
            font-size: %(font_size_base)s;
        }
        
        MangoLineEdit#mango_line_edit:focus {
            border: 1px solid %(primary_500)s;
            background-color: %(bg_100)s;
        }
        
        /* 按钮样式 */
        QPushButton#mango_push_button {
            border: %(border)s;
            color: %(text_100)s;
            border-radius: %(radius_full)s;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 %(neutral_50)s, stop: 1 %(neutral_100)s);
            padding: %(spacing_2)s %(spacing_4)s;
            font-family: %(font_family)s;
            font-size: %(font_size_base)s;
            font-weight: %(font_weight_semibold)s;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        QPushButton#mango_push_button:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 %(neutral_100)s, stop: 1 %(neutral_200)s);
            border: 1px solid %(primary_300)s;
            color: %(neutral_900)s;
            transform: translateY(-1px);
        }
        
        QPushButton#mango_push_button:pressed {
            background: %(primary_500)s;
            color: white;
            border: 1px solid %(primary_500)s;
            transform: translateY(0);
        }
        
        QPushButton#mango_push_button:disabled {
            background: %(neutral_100)s;
            color: %(neutral_400)s;
            border: 1px solid %(neutral_200)s;
            transform: none;
        }
        
        /* 主要按钮样式 */
        QPushButton#mango_push_button.primary {
            background: %(gradient_primary)s;
            color: white;
            border: none;
        }
        
        QPushButton#mango_push_button.primary:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 %(primary_600)s, stop: 1 %(primary_700)s);
            border: none;
            transform: translateY(-2px);
        }
        
        QPushButton#mango_push_button.primary:pressed {
            background: %(primary_700)s;
            transform: translateY(0);
        }
        
        /* 成功按钮样式 */
        QPushButton#mango_push_button.success {
            background: %(gradient_success)s;
            color: white;
            border: none;
        }
        
        QPushButton#mango_push_button.success:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 %(success_600)s, stop: 1 %(success_700)s);
            border: none;
            transform: translateY(-2px);
        }
        
        QPushButton#mango_push_button.success:pressed {
            background: %(success_700)s;
            transform: translateY(0);
        }
        
        /* 危险按钮样式 */
        QPushButton#mango_push_button.danger {
            background: %(gradient_danger)s;
            color: white;
            border: none;
        }
        
        QPushButton#mango_push_button.danger:hover {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 %(danger_600)s, stop: 1 %(danger_700)s);
            border: none;
            transform: translateY(-2px);
        }
        
        QPushButton#mango_push_button.danger:pressed {
            background: %(danger_700)s;
            transform: translateY(0);
        }
        
        /* 文本编辑器样式 */
        MangoTextEdit#mango_text_edit {
            background-color: %(bg_100)s;
            border-radius: %(radius)s;
            border: %(border)s;
            padding: %(spacing_2)s;
            selection-color: white;
            selection-background-color: %(primary_500)s;
            color: %(text_100)s;
            font-family: %(font_family)s;
            font-size: %(font_size_base)s;
        }
        
        MangoTextEdit#mango_text_edit:focus {
            border: 1px solid %(primary_500)s;
            background-color: %(bg_100)s;
        }
        
        /* 标签页样式 */
        MangoTabs#mango_tabs {
            background-color: %(bg_100)s;
            border-radius: %(radius_lg)s;
            border: %(border)s;
            padding: %(spacing_2)s;
        }
        
        /* 对话框样式 */
        MangoDialog#mango_dialog {
            background-color: %(bg_100)s;
            border-radius: %(radius_xl)s;
            border: %(border)s;
        }
        
        MangoDialog#mango_dialog::title {
            background-color: %(bg_100)s;
            color: %(text_100)s;
            border-bottom: %(border)s;
            padding: %(spacing_3)s;
            font-weight: %(font_weight_bold)s;
            font-size: %(font_size_lg)s;
        }
        
        /* 树形控件样式 */
        MangoTree#mango_tree {
            background-color: %(bg_100)s;
            border-radius: %(radius)s;
            border: %(border)s;
            color: %(text_100)s;
            font-family: %(font_family)s;
            font-size: %(font_size_base)s;
            padding: %(spacing_2)s;
        }
    
        MangoTree#mango_tree::item {
            padding: %(spacing_2)s %(spacing_3)s;
            border-radius: %(radius_sm)s;
        }
    
        MangoTree#mango_tree::item:selected {
            background-color: %(primary_100)s;
            color: %(text_100)s;
        }
        
        MangoTree#mango_tree::item:hover {
            background-color: %(bg_200)s;
        }
        
        /* 滑块样式 */
        QSlider::groove:horizontal {
            border: 1px solid %(bg_300)s;
            height: 4px;
            background: %(bg_200)s;
            border-radius: 2px;
        }
        
        QSlider::handle:horizontal {
            background: %(primary_500)s;
            border: 1px solid %(primary_700)s;
            width: 18px;
            height: 18px;
            border-radius: 9px;
            margin: -7px 0;
        }
        
        QSlider::sub-page:horizontal {
            background: %(primary_300)s;
            border-radius: 2px;
        }
        
        /* 复选框样式 */
        QCheckBox {
            color: %(text_100)s;
            font-family: %(font_family)s;
            font-size: %(font_size_base)s;
            spacing: %(spacing_2)s;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid %(bg_300)s;
            background-color: %(bg_100)s;
            border-radius: %(radius_sm)s;
        }
        
        QCheckBox::indicator:checked {
            background-color: %(primary_500)s;
            border: 1px solid %(primary_500)s;
        }
        
        QCheckBox::indicator:checked:after {
            content: "";
            position: absolute;
            width: 4px;
            height: 8px;
            border: 1px solid white;
            border-left: 0;
            border-top: 0;
            transform: rotate(45deg);
            left: 4px;
            top: 1px;
        }
        
        /* 单选按钮样式 */
        QRadioButton {
            color: %(text_100)s;
            font-family: %(font_family)s;
            font-size: %(font_size_base)s;
            spacing: %(spacing_2)s;
        }
        
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid %(bg_300)s;
            background-color: %(bg_100)s;
            border-radius: 8px;
        }
        
        QRadioButton::indicator:checked {
            background-color: %(primary_500)s;
            border: 1px solid %(primary_500)s;
        }
        
        QRadioButton::indicator:checked:after {
            content: "";
            position: absolute;
            width: 6px;
            height: 6px;
            background-color: white;
            border-radius: 3px;
            left: 5px;
            top: 5px;
        }
        
        /* 进度条样式 */
        QProgressBar {
            border: %(border)s;
            border-radius: %(radius)s;
            background-color: %(bg_200)s;
            text-align: center;
            color: %(text_100)s;
            font-size: %(font_size_xs)s;
        }
        
        QProgressBar::chunk {
            background-color: %(primary_500)s;
            border-radius: %(radius_sm)s;
        }
        
        /* 工具提示样式 */
        QToolTip {
            background-color: %(neutral_800)s;
            color: white;
            border: none;
            border-radius: %(radius_sm)s;
            padding: %(spacing_1)s %(spacing_2)s;
            font-family: %(font_family)s;
            font-size: %(font_size_xs)s;
        }
    """ % {
        # 主色调
        'primary_50': theme.primary_50,
        'primary_100': theme.primary_100,
        'primary_200': theme.primary_200,
        'primary_300': theme.primary_300,
        'primary_400': theme.primary_400,
        'primary_500': theme.primary_500,
        'primary_600': theme.primary_600,
        'primary_700': theme.primary_700,
        'primary_800': theme.primary_800,
        'primary_900': theme.primary_900,
        
        # 成功色
        'success_50': theme.success_50,
        'success_100': theme.success_100,
        'success_200': theme.success_200,
        'success_300': theme.success_300,
        'success_400': theme.success_400,
        'success_500': theme.success_500,
        'success_600': theme.success_600,
        'success_700': theme.success_700,
        'success_800': theme.success_800,
        'success_900': theme.success_900,
        
        # 警告色
        'warning_50': theme.warning_50,
        'warning_100': theme.warning_100,
        'warning_200': theme.warning_200,
        'warning_300': theme.warning_300,
        'warning_400': theme.warning_400,
        'warning_500': theme.warning_500,
        'warning_600': theme.warning_600,
        'warning_700': theme.warning_700,
        'warning_800': theme.warning_800,
        'warning_900': theme.warning_900,
        
        # 危险色
        'danger_50': theme.danger_50,
        'danger_100': theme.danger_100,
        'danger_200': theme.danger_200,
        'danger_300': theme.danger_300,
        'danger_400': theme.danger_400,
        'danger_500': theme.danger_500,
        'danger_600': theme.danger_600,
        'danger_700': theme.danger_700,
        'danger_800': theme.danger_800,
        'danger_900': theme.danger_900,
        
        # 中性色
        'neutral_50': theme.neutral_50,
        'neutral_100': theme.neutral_100,
        'neutral_200': theme.neutral_200,
        'neutral_300': theme.neutral_300,
        'neutral_400': theme.neutral_400,
        'neutral_500': theme.neutral_500,
        'neutral_600': theme.neutral_600,
        'neutral_700': theme.neutral_700,
        'neutral_800': theme.neutral_800,
        'neutral_900': theme.neutral_900,
        
        # 渐变色
        'gradient_primary': theme.gradient_primary,
        'gradient_success': theme.gradient_success,
        'gradient_danger': theme.gradient_danger,
        
        # 圆角
        'radius_none': theme.radius_none,
        'radius_sm': theme.radius_sm,
        'radius': theme.radius,
        'radius_md': theme.radius_md,
        'radius_lg': theme.radius_lg,
        'radius_xl': theme.radius_xl,
        'radius_2xl': theme.radius_2xl,
        'radius_3xl': theme.radius_3xl,
        'radius_full': theme.radius_full,
        
        # 间距
        'spacing_0': theme.spacing_0,
        'spacing_1': theme.spacing_1,
        'spacing_2': theme.spacing_2,
        'spacing_3': theme.spacing_3,
        'spacing_4': theme.spacing_4,
        'spacing_5': theme.spacing_5,
        'spacing_6': theme.spacing_6,
        'spacing_8': theme.spacing_8,
        'spacing_10': theme.spacing_10,
        'spacing_12': theme.spacing_12,
        
        # 字体大小
        'font_size_xs': theme.font_size_xs,
        'font_size_sm': theme.font_size_sm,
        'font_size_base': theme.font_size_base,
        'font_size_lg': theme.font_size_lg,
        'font_size_xl': theme.font_size_xl,
        'font_size_2xl': theme.font_size_2xl,
        'font_size_3xl': theme.font_size_3xl,
        
        # 字体粗细
        'font_weight_normal': theme.font_weight_normal,
        'font_weight_medium': theme.font_weight_medium,
        'font_weight_semibold': theme.font_weight_semibold,
        'font_weight_bold': theme.font_weight_bold,
        
        # 行高
        'line_height_normal': theme.line_height_normal,
        'line_height_tight': theme.line_height_tight,
        
        # 原有变量保持兼容
        'text_100': theme.text_100,
        'text_200': theme.text_200,
        'bg_100': theme.bg_100,
        'bg_200': theme.bg_200,
        'bg_300': theme.bg_300,
        'border': theme.border,
        'border_radius': theme.border_radius,
        'font_family': theme.font.family
    }


# 切换主题
def apply_theme(theme):
    qss_style = generate_qss(theme)
    app: QApplication = QApplication.instance()  # type: ignore
    if app is not None:
        app.setStyleSheet(qss_style)