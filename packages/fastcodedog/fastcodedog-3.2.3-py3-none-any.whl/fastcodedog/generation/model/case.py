# -*- coding: utf-8 -*-
from fastcodedog.context.model.case import Case as CaseContext
from fastcodedog.generation.base.call import Call
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.variable import Variable


class Case(Variable):
    def __init__(self, context: CaseContext = None, parent=None):
        super().__init__(context.name, context=context, parent=parent)
        self.title = context.title  # 标题
        self.whens = context.whens  # case条件列表

        self.value = self.get_value()
        self.comment = context.comment if context.comment else self.title

        self.add_possible_imports([
            Import('from sqlalchemy import case'),
        ])

    def get_value(self):
        """
        生成类似如下的代码:
        case(
            (result.is_(None), 0),
            (result == False, 1),
            (result == True, 2),
            else_=3
        )
        """
        case_params = []

        # 为每个when条件创建一个元组，自动分配数字值
        for index, when_condition in enumerate(self.whens):
            # 创建元组形式: (condition, value)
            case_params.append(f"({when_condition}, {index})")

        # 添加else_子句，值为条件数量
        case_params.append(f"else_={len(self.whens)}")

        return Call('case', params=case_params)

