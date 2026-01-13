# -*- coding: utf-8 -*-
import json5
import os

from fastcodedog.util.case_converter import camel_to_snake


def add_cases(model_directory, cases):
    """
    对应sqlalchemy的case，可用于order_by, filter, select, group_by, update等场景
    这些属性不保存到数据库，通过各种条件计算得到对应的值
    通过在model和schema中自定义属性的方法定义这些属性
    """
    for case in cases:
        module = case.get('module')
        model_name = case.get('model_name')
        name = case.get('name')
        if module and model_name and name:
            json_file = os.path.join(model_directory, module, f'{camel_to_snake(model_name)}.json5')
            data = json5.load(open(json_file, 'r', encoding='utf-8'))
            # 移除 case 中的 module 和 model_name
            case.pop('module')
            case.pop('model_name')
            # 确保 cases 键存在
            if 'cases' not in data:
                data['cases'] = {}
            data['cases'][name] = case
            json5.dump(data, open(json_file, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)

