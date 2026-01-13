# -*- coding: utf-8 -*-
from fastcodedog.context.api.oauth2 import OAuth2
from fastcodedog.context.contextbase import ContextBase
from typing import Any


class Config(ContextBase):
    class Param(ContextBase):
        def __init__(self):
            super().__init__()
            self.section = ''
            self.key = ''
            self.name = ''      # 是上级self.params的key，在需要使用之前要先反写
            self.type = 'str'
            self.required = False
            self.comment = ''
            self.default = None
            self._types['default'] = Any
            self.value = None
            self._types['value'] = Any


    def __init__(self):
        super().__init__()
        self.env_prefix = 'FASTCODEDOG_'
        self.params = {}
        self._types['params'] = Config.Param
