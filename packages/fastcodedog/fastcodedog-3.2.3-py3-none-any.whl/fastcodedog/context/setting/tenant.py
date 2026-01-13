# -*- coding: utf-8 -*-
from fastcodedog.context.contextbase import ContextBase


class Tenant(ContextBase):
    def __init__(self):
        super().__init__()
        self.enabled = False
        self.local_column_code = "tenant_id"
        self.foreign_table_code = "base_tenant"
        self.foreign_column_code = "id"
        self.ignore_tables = []  # 不需要租户隔离的表名单
        self._types['ignore_tables'] = str
