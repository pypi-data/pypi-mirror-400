# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class Case(ContextBase):
    def __init__(self):
        super().__init__()
        self.title = ''  # 标题，用于描述case的用途
        self.name = ''  # case属性名
        self.comment = ''  # 详细说明
        self.module = ''  # 所属模块
        self.model_name = ''  # 所属模型
        self.whens = []  # case条件列表，按顺序定义。自动指定数字和else_
        self._types['whens'] = str

