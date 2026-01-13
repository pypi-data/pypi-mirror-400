import os
from functools import lru_cache
from pathlib import Path
from typing import Union, Optional

import yaml
from fastapi.exceptions import ValidationException
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from fastgenerateapi.settings.etcd_settings import EtcdSettings
from fastgenerateapi.settings.redis_settings import RedisSettings
from fastgenerateapi.settings.app_settings import AppSettings
from fastgenerateapi.settings.system_settings import SystemSettings


class SettingsModel(BaseModel):
    # 应用配置
    app_settings: AppSettings = AppSettings()
    # 系统配置
    system_settings: SystemSettings = SystemSettings()
    # 缓存配置
    redis_settings: RedisSettings = RedisSettings()

    @classmethod
    def generate_file(
            cls,
            path='./.env',
            etcd_settings: Optional[EtcdSettings] = None,
    ):
        """
        生成配置文件
        .env 会增加前缀
        .yaml 忽略前缀
        :param path: 可选 .env / application.yaml
        :param etcd_settings:
        :return:
        """
        content = ''
        setting_models = cls.model_fields.copy()
        if path.__contains__('.env'):
            for k, v in setting_models.items():
                if isinstance(v, FieldInfo):
                    content += f"[{v.annotation.__name__}]\n"
                    env_prefix = v.annotation.model_config.get("env_prefix", "")
                    fields = v.annotation.model_fields.copy()
                    for k, v in fields.items():
                        field_name = f'{env_prefix}{k}'
                        if v.description is None:
                            content += f"{field_name}={v.default}\n"
                        else:
                            content += f"# {v.description}\n{field_name}={v.default}\n"
                    content += "\n"
        elif path.__contains__('.yaml'):
            for k, v in setting_models.items():
                if isinstance(v, FieldInfo):
                    content += f"[{v.annotation.__name__}]\n"
                    env_prefix = v.annotation.model_config.get("env_prefix", "")
                    fields = v.annotation.model_fields.copy()
                    for k, v in fields.items():
                        field_name = f'{env_prefix}{k}'
                        content += f"  {field_name}: {v.default}"
                        if v.description is None:
                            content += f"\n"
                        else:
                            content += f"  # {v.description}\n"
                    content += "\n"
        if etcd_settings and etcd_settings.ETCD_SETTING_KEY:
            etcd_settings.client.put(etcd_settings.ETCD_SETTING_KEY, content)
        else:
            with open(file=path, mode='w', encoding='utf-8') as f:
                f.writelines(content)

    @classmethod
    @lru_cache
    def get_global_settings(
            cls,
            path: Union[Path, str, None] = None,
    ):
        """
        get global settings and set into cache
        :param path: 指定本地文件，指定的文件不能用于修改 SettingsModel、EtcdSettings 的属性

        Etcd配置优先级：
            application.yaml > path指定文件 > .env
        其他属性优先级：
             application.yaml > path指定文件 > Etcd配置文件 > .env
            除了.env，其他都是yaml格式。同是yaml格式会覆盖
        :return:
        """
        data_dict = {}
        if path and path != "application.yaml":
            if not os.path.isfile(path):
                raise ValidationException(f"指定哦欸之文件【{path}】不存在")
            if str(path).endswith('.yaml'):
                with open(path, 'r', encoding='utf-8') as file:
                    data_dict.update(yaml.safe_load(file) or {})
            else:
                raise ValidationException("不支持指定非yaml格式")
        if os.path.isfile("application.yaml"):
            with open("application.yaml", 'r', encoding='utf-8') as file:
                data_dict.update(yaml.safe_load(file) or {})

        etcd_settings = EtcdSettings(**data_dict.get("EtcdSettings", {}))
        if etcd_settings.ETCD_SETTING_KEY:
            res, metadata = etcd_settings.client.get(etcd_settings.ETCD_SETTING_KEY)
            if not res:
                raise ValidationException("未读取到Etcd的配置文件")
            yaml_dict = yaml.safe_load(res)
            data_dict = {**yaml_dict, **data_dict}

        setting_models = cls.model_fields.copy()
        for k, v in setting_models.items():
            if isinstance(v, FieldInfo):
                env_prefix = None
                if hasattr(v.annotation, "Config") and v.annotation.Config.env_prefix:
                    env_prefix = v.annotation.Config.env_prefix
                if not env_prefix and hasattr(v.annotation, "model_config"):
                    env_prefix = v.annotation.model_config.get("env_prefix")
                if env_prefix:
                    annotation_dict = {
                        k_i.removeprefix(env_prefix): v_i for k_i, v_i in
                        data_dict.get(v.annotation.__name__, {}).items()
                    }
                else:
                    annotation_dict = data_dict.get(v.annotation.__name__, {})
                setattr(cls, k, v.annotation(**annotation_dict))

        return cls

    def watch(self):
        """
        监听文件或者etcd变化，待完善
        借用 etcd.watch(target)
        :return:
        """
        ...


settings = SettingsModel.get_global_settings()


if __name__ == '__main__':
    settings.generate_file()

