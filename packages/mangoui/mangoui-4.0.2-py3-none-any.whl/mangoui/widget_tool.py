# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-10-16 15:46
# @Author : 毛鹏
import json


class WidgetTool:

    @classmethod
    def remove_layout(cls, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                cls.remove_layout(item.layout())
                item.layout().deleteLater()

    @staticmethod
    def json_init_data(data: str | dict | list | None, save: bool = False):
        if not save:
            if data is None:
                return data
            elif isinstance(data, str):
                try:
                    parsed_data = json.loads(data)
                    return json.dumps(parsed_data, ensure_ascii=False, indent=4)
                except json.JSONDecodeError:
                    return data
            elif isinstance(data, dict) or isinstance(data, list):
                return json.dumps(data, ensure_ascii=False, indent=4)
        else:
            if data is None or data == '':
                return None
            else:
                return json.loads(data)
