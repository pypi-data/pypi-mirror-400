import time
from datetime import datetime
from typing import Type, Optional, Union, List, Callable

from fastapi import HTTPException
from pydantic import field_validator, model_validator
from pydantic.fields import FieldInfo
from tortoise import Model

from fastgenerateapi.api_view.mixin.dbmodel_mixin import DBModelMixin
from fastgenerateapi.pydantic_utils.base_model import alias_generator, BaseModel
from fastgenerateapi.settings.all_settings import settings


def get_field_info(value, description="", default_field_type=None) -> (Type, FieldInfo):
    if value.pk:
        return str, FieldInfo()

    required = False
    if value.field_type is None:
        if default_field_type:
            value.field_type = default_field_type
        else:
            value.field_type = str
    field_info_dict = {}
    if hasattr(value, "null") and value.null:
        field_type = Optional[value.field_type]
        field_info_dict["default"] = None
    else:
        field_type = value.field_type
        required = True
    field_info_dict["required"] = required

    if not required:
        if hasattr(value, "default") and not hasattr(value.default, '__call__'):
            field_info_dict.setdefault("default", value.default)
        else:
            field_info_dict["default"] = None
    if hasattr(value, "description"):
        field_info_dict.setdefault("description", description + (value.description or ""))
    if hasattr(value, "alias"):
        field_info_dict.setdefault("alias", value.alias)
    if hasattr(value, 'constraints'):
        constraints = getattr(value, 'constraints')
        if constraints:
            for key, val in constraints.items():
                field_info_dict.setdefault(key, val)
    if settings.app_settings.SWAGGER_OPEN_DEFAULT_EXAMPLES:
        examples = []
        if value.field_type == str:
            examples.append(value.description)
        elif value.field_type == int:
            if hasattr(value, "start_num"):
                examples.append(value.start_num)
            else:
                examples.append(0)
        elif value.field_type == datetime:
            examples.append(int(time.time() * 1000))
        field_info_dict.setdefault("examples", examples)
    return field_type, FieldInfo(**field_info_dict)


def get_dict_from_model_fields(model_class: Type[Model]) -> dict:
    all_fields_info = {}
    default_field_type = model_class._meta.fields_map.get("id").field_type
    for key, value in model_class._meta.fields_map.items():
        if key in model_class._meta.fk_fields:
            key += "_id"
        all_fields_info[key] = get_field_info(value, default_field_type=default_field_type)

    return all_fields_info


def get_field_info_from_model_class(model_class: Type[Model], field: str, description="") -> (Type, FieldInfo):
    if "__" not in field:
        value = model_class._meta.fields_map.get(field)
        if not value:
            return Optional[str], FieldInfo(default=None, description=f"{field}")
        return get_field_info(value, description=description)

    split_left_field = field.split("__", maxsplit=1)[0]
    field_info = model_class._meta.fields_map.get(split_left_field)
    if field_info:
        description += field_info.description or ""
    elif split_left_field.endswith("_id"):
        field_info = model_class._meta.fields_map.get(split_left_field.removesuffix("_id"))
        if field_info:
            description += field_info.description or ""

    model_class = DBModelMixin._get_foreign_key_relation_class(model_class, split_left_field)

    return get_field_info_from_model_class(model_class, field.split("__", maxsplit=1)[1], description)


def get_dict_from_pydanticmeta(model_class: Type[Model], data: Union[list, tuple, set]):
    fields_info = {}
    if not data:
        return fields_info
    for field in data:
        if isinstance(field, str):
            key_field = field
            field_type, field_info = get_field_info_from_model_class(model_class, field)
            if settings.app_settings.SCHEMAS_UNDERLINE_WHETHER_DOUBLE_TO_SINGLE:
                key_field = key_field.replace("__", "_")
            fields_info.setdefault(key_field, (field_type, field_info))
        elif isinstance(field, (tuple, list)):
            key_field = field[0]
            field_type, field_info = get_field_info_from_model_class(model_class, field[0])
            if len(field) == 2:
                if isinstance(field[1], str):
                    key_field = field[1]
                elif isinstance(field[1], FieldInfo):
                    field_info = field[1]
                else:
                    field_type = field[1]
            elif len(field) == 3:
                if isinstance(field[1], str):
                    key_field = field[1]
                    if isinstance(field[2], FieldInfo):
                        field_info = field[2]
                    else:
                        field_type = field[2]
                else:
                    field_type = field[1]
                    field_info = field[2]
            elif len(field) > 3:
                key_field = field[1]
                field_type = field[2]
                field_info = field[3]
            fields_info.setdefault(key_field, (field_type, field_info))
        else:
            raise NotImplemented
    return fields_info


def get_validate_dict() -> dict:

    def empty_str_to_none(v, values):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    validator_dict = {
        "empty_str_to_none": field_validator('*', mode='before')(empty_str_to_none)
    }

    return validator_dict


def get_validate_dict_from_fields(fields_info: dict) -> dict:
    validator_dict = {}

    def remove_blank_strings(v, values):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    for filed, field_tuple in fields_info.items():
        if field_tuple[0] == str:
            method_name = "check_%s" % filed
            # v1
            # validator_method = validator(filed, pre=True, allow_reuse=True)(remove_blank_strings)
            # v2
            validator_method = field_validator(filed, mode='before')(remove_blank_strings)
            validator_dict[method_name] = validator_method
    return validator_dict


class FieldValidateInfo(BaseModel):
    name: str
    is_required: bool
    description: str
    func: Callable


def get_field_validate_dict(infos: List[FieldValidateInfo]) -> dict:
    """
    字段做校验
    :param infos:
    :return:
    """
    if not infos:
        return {}

    def _func(i: FieldValidateInfo):
        def func(cls, value):
            is_empty = value is None or value == ''
            if i.is_required and is_empty:
                raise HTTPException(status_code=422, detail=i.description+"不能为空")
            if not is_empty and not i.func(value):
                raise HTTPException(status_code=422, detail=i.description+"校验不通过")
            return value
        return func

    return {"check_"+info.name: field_validator(info.name)(_func(info)) for info in infos}


def get_model_validate_text_to_list(fields: Optional[List[str]]) -> dict:
    """
    详情列表用于返回
    :param fields:
    :return:
    """
    if not fields:
        return {}
    def func(cls, data):
        if isinstance(data, dict):
            for field in fields:
                value_str = data.get(field, None)
                if isinstance(value_str, (list, tuple, set)):
                    field_value = list(value_str)
                elif isinstance(value_str, str):
                    field_value = value_str.split(settings.app_settings.TEXT_TO_LIST_SPLIT_VALUE)
                else:
                    field_value = value_str
                data[field] = field_value
        else:
            for field in fields:
                if hasattr(data, field):
                    value_str = getattr(data, field)
                    if isinstance(value_str, (list, tuple, set)):
                        field_value = list(value_str)
                    elif isinstance(value_str, str):
                        field_value = getattr(data, field).split(settings.app_settings.TEXT_TO_LIST_SPLIT_VALUE)
                    else:
                        field_value = []
                    setattr(data, field, field_value)
        return data

    return {
        "text_to_list_func": model_validator(mode='before')(func)
    }


def get_model_validate_list_to_text(fields: Optional[List[str]]) -> dict:
    """
    创建修改用于保存
    :param fields:
    :return:
    """
    if not fields:
        return {}
    def func(cls, data: dict):
        if isinstance(data, dict):
            for field in fields:
                if field not in data and alias_generator:
                    field = alias_generator(field)
                value_list = data.get(field, None)
                if isinstance(value_list, (list, tuple, set)):
                    field_value = settings.app_settings.TEXT_TO_LIST_SPLIT_VALUE.join(list(value_list))
                elif isinstance(value_list, str):
                    field_value = value_list
                else:
                    field_value = None
                data[field] = field_value
        else:
            for field in fields:
                if not hasattr(data, field) and alias_generator:
                    field = alias_generator(field)
                if hasattr(data, field):
                    value_list = getattr(data, field)
                    if isinstance(value_list, (list, tuple, set)):
                        field_value = settings.app_settings.TEXT_TO_LIST_SPLIT_VALUE.join(list(value_list))
                    elif isinstance(value_list, str):
                        field_value = value_list
                    else:
                        field_value = None
                    setattr(data, field, field_value)
        return data

    return {
        "list_to_text_func": model_validator(mode='before')(func)
    }

