from typing import Type, Optional, Dict, List

from pydantic.fields import FieldInfo

from fastgenerateapi.data_type.data_type import T

class ToolMixin:

    @staticmethod
    def reserve_dict(data: dict) -> dict:
        """
        字典key,value互转
        """
        result = {}
        for key, val in data.items():
            result[val] = key
        return result

    @staticmethod
    def get_schema_alise_to_name(schema: Optional[Type[T]]) -> Dict[str, str]:
        """
        返回 alias 对 name 的字典
        :param schema:
        :return:
        """
        alias_dict = {}
        if schema and hasattr(schema, "model_fields"):
            for field, info in schema.model_fields.items():
                alias_dict[info.alias or field] = field

        return alias_dict

    @staticmethod
    def get_schema_alise_to_field_info(schema: Optional[Type[T]]) -> Dict[str, FieldInfo]:
        """
        返回 alias 对 FieldInfo 的字典
        :param schema:
        :return:
        """
        alias_dict = {}
        if schema and hasattr(schema, "model_fields"):
            for field, info in schema.model_fields.items():
                if info.alias:
                    alias_dict[info.alias] = info
                alias_dict[field] = info

        return alias_dict


