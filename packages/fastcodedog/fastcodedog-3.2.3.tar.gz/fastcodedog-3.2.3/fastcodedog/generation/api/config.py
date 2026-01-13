# -*- coding: utf-8 -*-
from fastcodedog.context.context import ctx_instance
from fastcodedog.generation.base.file import File
from fastcodedog.generation.base.function import Function
from fastcodedog.generation.base.location_finder import LocationFinder
from fastcodedog.generation.base.text import Text
from fastcodedog.generation.base.variable import Variable


class Config(File):
    def __init__(self, comment=None, possible_imports: list | str = None, parent=None):
        super().__init__('config',
                         file_path=LocationFinder.get_path('config', 'config'),
                         package=LocationFinder.get_package('config', 'config'), comment=comment, parent=parent)
        self.ini_file = self.file_path[:-3] + '.ini'
        self.sections = {}
        self._convert_sections()
        self._init_blocks_and_imports()
        self.ini_content = self._get_ini_content()

    def _convert_sections(self):
        for name, param in ctx_instance.config.params.items():
            if param.section not in self.sections:
                self.sections[param.section] = {}
            param.name = name
            self.sections[param.section][param.key] = param

    def _init_blocks_and_imports(self):
        parse_config = Function('parse_config',
                                params={'config_path': Function.Parameter('config_path', type='str', default_value='config.ini')},
                                return_type='Dict[str, Dict[str, Any]]', comment='解析配置，忽略未预定义的命令行参数，返回嵌套字典')
        parse_config.blocks.append(Text(f"""# 1. 预设配置项：类型和默认值"""))
        section_text = ""
        for name, params in self.sections.items():
            if len(section_text) > 0:
                section_text += ",\n"
            section_text += f"""'{name}': {{"""     # section start
            is_first_param = True
            for key, param in params.items():
                if not is_first_param:
                    section_text += ",\n"
                is_first_param = False
                section_text += f"""'{key}': {{"""    # param start
                section_text += f"""'type': {param.type}, 'default': {repr(param.default)}"""
                section_text += f"""}}"""           # param end
            section_text += f"""}}"""               # section end
        parse_config.blocks.append(Text(f"""PRESETS = {{ {section_text} }}"""))
        parse_config.blocks.append(Text(f"""
# 2. 读取ini文件
ini_config: Dict[str, Dict[str, Any]] = {{}}
config = configparser.ConfigParser()
config.read(config_path, encoding="utf-8")

for section in PRESETS:
    ini_config[section] = {{}}
    if section in config:
        for key, meta in PRESETS[section].items():
            if key in config[section]:
                raw_val = config[section][key]
                ini_config[section][key] = (
                    meta["type"](raw_val)
                    if meta["type"] is not bool
                    else (raw_val.lower() == "true")
                )

# 3 从环境变量覆盖配置（优先于ini文件）
# 支持的环境变量格式：{ctx_instance.config.env_prefix}_{{SECTION}}_{{KEY}}（全部大写）
for section, keys in PRESETS.items():
    for key, meta in keys.items():
        env_name = f"{ctx_instance.config.env_prefix}_{{section}}_{{key}}".upper()
        if env_name in os.environ:
            raw_val = os.environ[env_name]
            # 保证 section 存在
            ini_config.setdefault(section, {{}})
            ini_config[section][key] = (
                meta["type"](raw_val)
                if meta["type"] is not bool
                else (raw_val.lower() == "true")
            )

# 4. 配置命令行解析器（参数名：section_key）
parser = argparse.ArgumentParser(description="命令行参数")
for section, keys in PRESETS.items():
    for key, meta in keys.items():
        arg_name = f"{{section}}_{{key}}"
        default_val = ini_config[section].get(key, meta["default"])
        parser.add_argument(
            f"--{{arg_name}}",
            type=meta["type"] if meta["type"] is not bool else (lambda s: s.lower() == "true"),
            default=default_val
        )

# 5. 解析参数（关键：用parse_known_args()忽略未定义参数）
args, unknown = parser.parse_known_args()  # unknown接收未定义的参数，不报错
# 可选：打印忽略的参数（调试用）
# if unknown:
#     print(f"忽略未预定义的参数：{{unknown}}")

# 6. 转换为嵌套字典
result: Dict[str, Dict[str, Any]] = {{}}
for section, keys in PRESETS.items():
    result[section] = {{}}
    for key in keys:
        arg_name = f"{{section}}_{{key}}"
        result[section][key] = getattr(args, arg_name)

return result
""", possible_imports=['from typing import Any', 'from typing import Dict', 'import argparse', 'import configparser', 'import os']))
        self.blocks.append(parse_config)

        self.blocks.append(Variable('config_path', value="os.path.join(os.path.dirname(__file__), 'config.ini')", comment='固定配置文件位置', possible_imports='import os'))
        self.blocks.append(Variable('configs', value='parse_config(config_path)', comment='解析配置'))
        self.blocks.append(Text(f"""# 显式定义所有配置变量"""))
        for name, param in ctx_instance.config.params.items():
            self.blocks.append(Variable(name, value=f"configs['{param.section}']['{param.key}']"))


    def save(self):
        super().save()
        open(self.ini_file, 'w', encoding='utf-8').write(self.ini_content)

    def _get_ini_content(self):
        content = "; 可以通过ini文件、环境变量和命令行三种方式配置参数，优先级依次递增\n"
        content += "; 通过uvicorn或者celery启动时，日志配置仍然以本配置为准，建议通过环境变量设置不同进程的不同参数\n"
        for section, params in self.sections.items():
            if section.startswith('_'):
                continue
            content += f"[{section}]\n"

            for key, param in params.items():
                if param.comment:
                    content += f"; {param.comment}\n"
                content += f"; 环境变量{ctx_instance.config.env_prefix.upper()}_{section.upper()}_{key.upper()}\n"
                if param.value is not None:
                    content += f"{param.key} = {param.value}\n"
                else:
                    content += f"; {param.key} = {param.default}\n"

        return content

