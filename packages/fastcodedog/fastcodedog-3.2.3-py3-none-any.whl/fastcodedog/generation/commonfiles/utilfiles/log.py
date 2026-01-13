# -*- coding: utf-8 -*-
import os

from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.api.config import Config
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.required_import import Import
from fastcodedog.generation.base.text import Text
from fastcodedog.generation.base.variable import Variable


class Log(File):
    def __init__(self):
        super().__init__(name='log',
                         file_path=os.path.join(ctx_instance.project.directory, 'util', 'log.py'),
                         package=f'{ctx_instance.project.package}.util.log')
        self.blocks.append(Variable('logger_', None))
        self.blocks.append(self.get_get_logger())
        self.blocks.append(self.get_enable_console_log())
        self.blocks.append(self.get_reinit_logger())
        self.blocks.append(Variable('logger', value='get_logger()'))

    def get_get_logger(self):
        function = Function('get_logger')
        content =f"""global logger_
if logger_:
    return logger_

logger_ = logging.getLogger()
if logger_.hasHandlers():
    logger_.handlers.clear()
logger_.setLevel(log_level)

rotating_file_handler = ConcurrentRotatingFileHandler(log_filename, mode='a', maxBytes=int(log_max_bytes),
                                                      backupCount=int(log_backup_count), encoding=log_encoding)
rotating_file_handler.setLevel(log_level)
rotating_file_handler.setFormatter(logging.Formatter(log_format, datefmt=log_datefmt))
logger_.addHandler(rotating_file_handler)

if log_console:
    enable_console_log(logger_)

return logger_
        """
        function.blocks.append(Text(content, possible_imports=['import logging', 'from concurrent_log_handler import ConcurrentRotatingFileHandler',
                                   Import('logging_config', Config().package), Import('log_filename', Config().package), Import('log_level', Config().package), Import('log_encoding', Config().package), Import('log_datefmt', Config().package), Import('log_format', Config().package), Import('log_max_bytes', Config().package), Import('log_backup_count', Config().package), Import('log_console', Config().package)]))
        return function

    def get_enable_console_log(self):
        function = Function('enable_console_log', possible_imports=['import logging',
                                                                    Import('logging_config', Config().package)])
        function.params['logger_'] = Function.Parameter('logger_', nullable=False)
        content = f"""console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(logging.Formatter(log_format))
logger_.addHandler(console_handler)
"""
        function.blocks.append(Text(content, possible_imports=[Import('log_level', Config().package), Import('log_format', Config().package)]))
        return function


    def get_reinit_logger(self):
        function = Function('reinit_logger')
        content = f"""global logger_, logger
logger_ = None
logger = get_logger()"""
        function.blocks.append(Text(content))
        return function
