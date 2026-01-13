# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-11-02 21:24
# @Author : 毛鹏

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

# 从具体的组件模块中导入所需的组件
from mangoui.widgets.input import (
    MangoTimeEdit, MangoCascade, MangoCheckBox, MangoComboBox, 
    MangoLineEdit, MangoPushButton, MangoSlider, MangoTextEdit, 
    MangoToggle, MangoSpinBox, MangoDoubleSpinBox, MangoDateEdit, 
    MangoDateTimeEdit, MangoRadioButton, MangoPlainTextEdit, 
    MangoDial, MangoFontComboBox
)
from mangoui.widgets.container import MangoCard
from mangoui.widgets.layout import (
    MangoVBoxLayout, MangoHBoxLayout, MangoFormLayout, MangoGridLayout
)
from mangoui.models.models import CascaderModel, ComboBoxDataModel
from mangoui.settings.settings import THEME


class InputPage(QWidget):
    cascade_data = [{"value": 8, "label": "智投", "parameter": None, "children": [
        {"value": 13, "label": "新智投", "parameter": None,
         "children": [{"value": 107, "label": "登录", "parameter": None, "children": []},
                      {"value": 106, "label": "项目", "parameter": None, "children": []},
                      {"value": 105, "label": "小红书实时看版", "parameter": None, "children": []},
                      {"value": 104, "label": "报数助手", "parameter": None, "children": []},
                      {"value": 103, "label": "用户中心", "parameter": None, "children": []},
                      {"value": 102, "label": "首页", "parameter": None, "children": []}]},
        {"value": 6, "label": "老智投", "parameter": None,
         "children": [{"value": 93, "label": "小红星日报-搜索推广", "parameter": None, "children": []},
                      {"value": 92, "label": "小红星日报-信息流", "parameter": None, "children": []},
                      {"value": 91, "label": "登录", "parameter": None, "children": []}]}]},
                    {"value": 4, "label": "DESK", "parameter": None,
                     "children": [{"value": 4, "label": "ZDesk-二代", "parameter": None, "children": []},
                                  {"value": 1, "label": "ZDesk-低代码", "parameter": None,
                                   "children": [{"value": 81, "label": "收票单", "parameter": None, "children": []},
                                                {"value": 80, "label": "供应商管理", "parameter": None, "children": []},
                                                {"value": 79, "label": "供应商付款单", "parameter": None,
                                                 "children": []},
                                                {"value": 78, "label": "垫款管理", "parameter": None, "children": []},
                                                {"value": 77, "label": "低代码后台", "parameter": None, "children": []},
                                                {"value": 76, "label": "二代-充值申请", "parameter": None,
                                                 "children": []},
                                                {"value": 75, "label": "二代系统", "parameter": None, "children": []},
                                                {"value": 74, "label": "保证金付款单", "parameter": None,
                                                 "children": []},
                                                {"value": 73, "label": "供应商政策", "parameter": None, "children": []},
                                                {"value": 72, "label": "供应商列表", "parameter": None, "children": []},
                                                {"value": 71, "label": "常规授信设置", "parameter": None,
                                                 "children": []},
                                                {"value": 70, "label": "信用评级设置", "parameter": None,
                                                 "children": []},
                                                {"value": 69, "label": "临时垫款设置", "parameter": None,
                                                 "children": []},
                                                {"value": 68, "label": "巨量行业对应关系", "parameter": None,
                                                 "children": []},
                                                {"value": 67, "label": "销售指导政策设置", "parameter": None,
                                                 "children": []},
                                                {"value": 66, "label": "开户银行列表", "parameter": None,
                                                 "children": []},
                                                {"value": 65, "label": "结算方式推单设置", "parameter": None,
                                                 "children": []},
                                                {"value": 64, "label": "系统单据链路设置", "parameter": None,
                                                 "children": []},
                                                {"value": 63, "label": "线索池管理", "parameter": None, "children": []},
                                                {"value": 62, "label": "媒体平台/业务线/执行部门对应关系",
                                                 "parameter": None, "children": []},
                                                {"value": 61, "label": "供应商服务费用单", "parameter": None,
                                                 "children": []},
                                                {"value": 60, "label": "其他服务费用单", "parameter": None,
                                                 "children": []},
                                                {"value": 59, "label": "运营服务费用单", "parameter": None,
                                                 "children": []},
                                                {"value": 58, "label": "运营结算", "parameter": None, "children": []},
                                                {"value": 57, "label": "勾稽", "parameter": None, "children": []},
                                                {"value": 56, "label": "其他结算", "parameter": None, "children": []},
                                                {"value": 55, "label": "项目结算", "parameter": None, "children": []},
                                                {"value": 54, "label": "消耗结算", "parameter": None, "children": []},
                                                {"value": 53, "label": "充值结算", "parameter": None, "children": []},
                                                {"value": 52, "label": "消耗匹配明细", "parameter": None,
                                                 "children": []},
                                                {"value": 51, "label": "消耗同步", "parameter": None, "children": []},
                                                {"value": 50, "label": "营销点评列表", "parameter": None,
                                                 "children": []},
                                                {"value": 49, "label": "媒体账户关系组", "parameter": None,
                                                 "children": []},
                                                {"value": 48, "label": "媒体账户列表", "parameter": None,
                                                 "children": []},
                                                {"value": 47, "label": "媒体账户绑定", "parameter": None,
                                                 "children": []},
                                                {"value": 42, "label": "预收款管理", "parameter": None, "children": []},
                                                {"value": 31, "label": "合同管理", "parameter": None, "children": []},
                                                {"value": 30, "label": "非充值模块", "parameter": None, "children": []},
                                                {"value": 29, "label": "流水管理", "parameter": None, "children": []},
                                                {"value": 27, "label": "商机管理", "parameter": None, "children": []},
                                                {"value": 26, "label": "客户管理", "parameter": None, "children": []},
                                                {"value": 25, "label": "客资管理", "parameter": None, "children": []},
                                                {"value": 22, "label": "充值业务", "parameter": None, "children": []},
                                                {"value": 13, "label": "登录", "parameter": None, "children": []}]}]},
                    {"value": 3, "label": "CDXP", "parameter": None,
                     "children": [{"value": 11, "label": "GrowKnows", "parameter": None, "children": []}]},
                    {"value": 1, "label": "AIGC", "parameter": None,
                     "children": [{"value": 12, "label": "AIGC-SaaS", "parameter": None, "children": []},
                                  {"value": 10, "label": "AIGC-TMS", "parameter": None, "children": []},
                                  {"value": 7, "label": "AIGC日报", "parameter": None,
                                   "children": [{"value": 35, "label": "首页", "parameter": None, "children": []},
                                                {"value": 11, "label": "笔记历史", "parameter": None, "children": []},
                                                {"value": 10, "label": "家具", "parameter": None, "children": []},
                                                {"value": 9, "label": "装修", "parameter": None, "children": []},
                                                {"value": 8, "label": "配饰", "parameter": None, "children": []},
                                                {"value": 7, "label": "服饰", "parameter": None, "children": []},
                                                {"value": 6, "label": "品牌管理", "parameter": None, "children": []},
                                                {"value": 5, "label": "创作记录", "parameter": None, "children": []},
                                                {"value": 4, "label": "关键字", "parameter": None, "children": []},
                                                {"value": 3, "label": "信息流", "parameter": None, "children": []},
                                                {"value": 2, "label": "日报生成", "parameter": None, "children": []},
                                                {"value": 1, "label": "登录", "parameter": None, "children": []}]},
                                  {"value": 5, "label": "AIGC-SaaS-C端", "parameter": None,
                                   "children": [{"value": 97, "label": "文生图", "parameter": None, "children": []},
                                                {"value": 96, "label": "权益兑换", "parameter": None, "children": []},
                                                {"value": 95, "label": "智豆管理", "parameter": None, "children": []},
                                                {"value": 94, "label": "会员权益", "parameter": None, "children": []},
                                                {"value": 89, "label": "AI课堂", "parameter": None, "children": []},
                                                {"value": 88, "label": "知识库", "parameter": None, "children": []},
                                                {"value": 87, "label": "历史记录", "parameter": None, "children": []},
                                                {"value": 86, "label": "应用", "parameter": None, "children": []},
                                                {"value": 82, "label": "登录", "parameter": None, "children": []}]},
                                  {"value": 3, "label": "AIGC-WEB", "parameter": None, "children": []},
                                  {"value": 2, "label": "AIGC-SaaS", "parameter": None,
                                   "children": [{"value": 85, "label": "AI课堂", "parameter": None, "children": []},
                                                {"value": 84, "label": "历史记录", "parameter": None, "children": []},
                                                {"value": 83, "label": "应用", "parameter": None, "children": []},
                                                {"value": 45, "label": "语义搜索", "parameter": None, "children": []},
                                                {"value": 43, "label": "模版市场", "parameter": None, "children": []},
                                                {"value": 34, "label": "Flow列表", "parameter": None, "children": []},
                                                {"value": 33, "label": "所有模板", "parameter": None, "children": []},
                                                {"value": 32, "label": "模板管理", "parameter": None, "children": []},
                                                {"value": 24, "label": "创作模板", "parameter": None, "children": []},
                                                {"value": 21, "label": "小红书运营百事通", "parameter": None,
                                                 "children": []},
                                                {"value": 20, "label": "知识库", "parameter": None, "children": []},
                                                {"value": 19, "label": "文档分类", "parameter": None, "children": []},
                                                {"value": 18, "label": "个人中心", "parameter": None, "children": []},
                                                {"value": 17, "label": "首页", "parameter": None, "children": []},
                                                {"value": 16, "label": "文档库", "parameter": None, "children": []},
                                                {"value": 15, "label": "服饰达人", "parameter": None, "children": []},
                                                {"value": 14, "label": "登录", "parameter": None, "children": []}]}]}]
    combo_box_data = [{"id": 0, "name": "高"}, {"id": 1, "name": "中"}, {"id": 2, "name": "低"},
                      {"id": 3, "name": "极低"}]

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QVBoxLayout(self)

        # 创建滚动区域以容纳所有组件
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        
        # 标题
        title = QLabel("输入组件展示")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        self.scroll_layout.addWidget(title)

        # 使用网格布局组织所有组件，提高空间利用率
        self.components_grid = MangoGridLayout()
        self.components_grid.setColumnStretch(1, 1)
        self.components_grid.setColumnStretch(3, 1)
        
        # 原有组件 - 第一行
        self.mango_time_edit = MangoTimeEdit()
        self.components_grid.addWidget(QLabel("时间编辑器:"), 0, 0)
        self.components_grid.addWidget(self.mango_time_edit, 0, 1)
        
        self.mango_cascade = MangoCascade('多级选择', CascaderModel.get_model(self.cascade_data))
        self.components_grid.addWidget(QLabel("级联选择器:"), 0, 2)
        self.components_grid.addWidget(self.mango_cascade, 0, 3)
        
        # 第二行
        self.mango_checkbox = MangoCheckBox()
        self.components_grid.addWidget(QLabel("复选框:"), 1, 0)
        self.components_grid.addWidget(self.mango_checkbox, 1, 1)
        
        self.mango_combobox = MangoComboBox('选择框', ComboBoxDataModel.get_model(self.combo_box_data))
        self.components_grid.addWidget(QLabel("下拉选择框:"), 1, 2)
        self.components_grid.addWidget(self.mango_combobox, 1, 3)
        
        # 第三行
        self.mango_line_edit = MangoLineEdit('请输入内容')
        self.components_grid.addWidget(QLabel("单行文本输入框:"), 2, 0)
        self.components_grid.addWidget(self.mango_line_edit, 2, 1)
        
        self.mango_push_button = MangoPushButton('按钮')
        self.components_grid.addWidget(QLabel("按钮:"), 2, 2)
        self.components_grid.addWidget(self.mango_push_button, 2, 3)
        
        # 第四行
        self.mango_slider = MangoSlider()
        self.components_grid.addWidget(QLabel("滑块:"), 3, 0)
        self.components_grid.addWidget(self.mango_slider, 3, 1)
        
        self.mango_toggle = MangoToggle()
        self.components_grid.addWidget(QLabel("开关:"), 3, 2)
        self.components_grid.addWidget(self.mango_toggle, 3, 3)
        
        # 第五行
        self.mango_text_edit = MangoTextEdit('多行输入框')
        self.components_grid.addWidget(QLabel("多行文本输入框:"), 4, 0)
        self.components_grid.addWidget(self.mango_text_edit, 4, 1)
        
        # 新增组件 - 第六行
        self.mango_spin_box = MangoSpinBox()
        self.mango_spin_box.setValue(10)
        self.components_grid.addWidget(QLabel("整数输入框:"), 5, 0)
        self.components_grid.addWidget(self.mango_spin_box, 5, 1)
        
        self.mango_double_spin_box = MangoDoubleSpinBox()
        self.mango_double_spin_box.setValue(3.14)
        self.components_grid.addWidget(QLabel("浮点数输入框:"), 5, 2)
        self.components_grid.addWidget(self.mango_double_spin_box, 5, 3)
        
        # 第七行
        self.mango_date_edit = MangoDateEdit()
        self.components_grid.addWidget(QLabel("日期编辑器:"), 6, 0)
        self.components_grid.addWidget(self.mango_date_edit, 6, 1)
        
        self.mango_date_time_edit = MangoDateTimeEdit()
        self.components_grid.addWidget(QLabel("日期时间编辑器:"), 6, 2)
        self.components_grid.addWidget(self.mango_date_time_edit, 6, 3)
        
        # 第八行
        self.mango_radio_button1 = MangoRadioButton("选项1")
        self.mango_radio_button2 = MangoRadioButton("选项2")
        self.mango_radio_button_group = QButtonGroup()
        self.mango_radio_button_group.addButton(self.mango_radio_button1)
        self.mango_radio_button_group.addButton(self.mango_radio_button2)
        
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(QLabel("单选按钮:"))
        radio_layout.addWidget(self.mango_radio_button1)
        radio_layout.addWidget(self.mango_radio_button2)
        radio_layout.addStretch()
        radio_widget = QWidget()
        radio_widget.setLayout(radio_layout)
        self.components_grid.addWidget(radio_widget, 7, 0, 1, 4)
        
        # 第九行
        self.mango_plain_text_edit = MangoPlainTextEdit("纯文本编辑器")
        self.components_grid.addWidget(QLabel("纯文本编辑器:"), 8, 0)
        self.components_grid.addWidget(self.mango_plain_text_edit, 8, 1)
        
        self.mango_dial = MangoDial()
        self.mango_dial.setRange(0, 100)
        self.mango_dial.setValue(50)
        self.components_grid.addWidget(QLabel("刻度盘:"), 8, 2)
        self.components_grid.addWidget(self.mango_dial, 8, 3)
        
        # 第十行
        self.mango_font_combo_box = MangoFontComboBox()
        self.components_grid.addWidget(QLabel("字体下拉框:"), 9, 0)
        self.components_grid.addWidget(self.mango_font_combo_box, 9, 1)
        
        self.scroll_layout.addLayout(self.components_grid)

        # 设置滚动区域
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)