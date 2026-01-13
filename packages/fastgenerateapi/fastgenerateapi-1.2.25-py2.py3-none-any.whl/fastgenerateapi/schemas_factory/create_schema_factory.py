from typing import Type, Union, Optional, List

from fastgenerateapi.settings.all_settings import settings

from fastgenerateapi.pydantic_utils.base_model import model_config
from pydantic import create_model
from tortoise import Model

from fastgenerateapi.data_type.data_type import T
from fastgenerateapi.schemas_factory.common_function import get_dict_from_model_fields, get_dict_from_pydanticmeta, \
    get_validate_dict_from_fields, get_model_validate_list_to_text, FieldValidateInfo, get_field_validate_dict


def create_schema_factory(
        model_class: Type[Model],
        include: Union[list, tuple, set] = None,
        extra_include: Union[list, tuple, set] = None,
        exclude: Union[list, tuple, set] = None,
        frozen_exclude: Union[list, tuple, set] = ("created_at", "updated_at", "modified_at"),
        pydantic_meta: Optional[bool] = True,
        pydantic_meta_include: Union[list, tuple, set] = None,
        pydantic_meta_exclude: Optional[bool] = True,
        pydantic_meta_save_include: Optional[bool] = True,
        pydantic_meta_save_exclude: Optional[bool] = True,
        pydantic_meta_create_include: Optional[bool] = True,
        pydantic_meta_create_exclude: Optional[bool] = True,
        pydantic_meta_save_validate: Optional[bool] = True,
        pydantic_meta_create_validate: Optional[bool] = True,
        pydantic_meta_text_to_list: Optional[bool] = True,
        name: Optional[str] = None
) -> Type[T]:
    """
    Is used to create a CreateSchema
    固定排除 逻辑删除字段
    会默认添加模型下 PydanticMeta 设置的相关属性
    - include: 增改详情列表通用，指定包含字段，不指定默认包含所有字段
    - exclude： 增改详情列表通用，指定排除字段
    - save_include: 增改通用，额外添加字段
    - save_exclude: 增改通用，指定排除字段
    - create_include: 增使用，额外添加字段
    - create_exclude: 增使用，指定排除字段
    - save_validate: 增改通用，指定字段做校验
    - create_validate: 增使用，指定字段做校验

    逻辑顺序：合并所有include和exclude，排除include下包含的exclude字段

    参数类型可选
    - include类型：
        - 字符串：【模型存在字段】自动生成，【模型不存在字段】默认字符串类型，无注释
        - 2个值：
            - (字符串, 类型int): 指定导出类型
            - (字符串, FieldInfo()):
            - (字符串1, 字符串2): 导出字段重命名。例如 ("name", "export_name")
        - 3个值：
            - (字符串1, 字符串2, 类型int):
            - (字符串, 字符串2, FieldInfo()):
            - (字符串, 类型int, FieldInfo()):
        - 4个值：
            - (字符串1, 字符串2, 类型int, FieldInfo()):
    - exclude类型：仅字符串

    示例：
    class model_class:
        ...

        PydanticMeta:
            include = []
            exclude = []
            save_include = [
                ("item_id_list", List[str], FieldInfo(description="多对多关联id列表")),
            ]
            save_exclude = ["ignore_field"]
            save_validate = [("phone", phone_validate), ("id_card", id_card_validate)]
            create_include = ["create_user"]
            create_exclude = []
            create_validate = []
    """
    all_fields_info = get_dict_from_model_fields(model_class)

    include_fields = set()
    exclude_fields = set()
    text_to_list_fields = set()
    validate_field_info = []
    if include:
        include_fields_dict = get_dict_from_pydanticmeta(model_class, include)
        all_fields_info.update(include_fields_dict)
        include_fields.update(include_fields_dict.keys())
    elif pydantic_meta and hasattr(model_class, "PydanticMeta"):
        if pydantic_meta_include:
            include_fields_dict = get_dict_from_pydanticmeta(model_class, pydantic_meta_include)
            all_fields_info.update(include_fields_dict)
            include_fields.update(include_fields_dict.keys())
        elif hasattr(model_class.PydanticMeta, "include"):
            include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.include)
            all_fields_info.update(include_fields_dict)
            include_fields.update(include_fields_dict.keys())
        else:
            include_fields.update(all_fields_info.keys())
        if pydantic_meta_exclude and hasattr(model_class.PydanticMeta, "exclude"):
            exclude_fields.update(model_class.PydanticMeta.exclude)
        if pydantic_meta_save_include and hasattr(model_class.PydanticMeta, "save_include"):
            save_include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.save_include)
            all_fields_info.update(save_include_fields_dict)
            include_fields.update(save_include_fields_dict.keys())
        if pydantic_meta_create_include and hasattr(model_class.PydanticMeta, "create_include"):
            create_include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.create_include)
            all_fields_info.update(create_include_fields_dict)
            include_fields.update(create_include_fields_dict.keys())
        if pydantic_meta_save_exclude and  hasattr(model_class.PydanticMeta, "save_exclude"):
            exclude_fields.update(model_class.PydanticMeta.save_exclude)
        if pydantic_meta_create_exclude and hasattr(model_class.PydanticMeta, "create_exclude"):
            exclude_fields.update(model_class.PydanticMeta.create_exclude)
        if pydantic_meta_save_validate and hasattr(model_class.PydanticMeta, "save_validate"):
            for validate in model_class.PydanticMeta.save_validate:
                file_type, file_info = all_fields_info.get(validate[0])
                validate_field_info.append(FieldValidateInfo(
                    name=validate[0],
                    is_required=file_info.is_required(),
                    description=file_info.description,
                    func=validate[1],
                ))
        if pydantic_meta_create_validate and hasattr(model_class.PydanticMeta, "create_validate"):
            for validate in model_class.PydanticMeta.create_validate:
                file_type, file_info = all_fields_info.get(validate[0])
                validate_field_info.append(FieldValidateInfo(
                    name=validate[0],
                    is_required=file_info.is_required(),
                    description=file_info.description,
                    func=validate[1],
                ))
        if pydantic_meta_text_to_list and hasattr(model_class.PydanticMeta, "text_to_list"):
            text_to_list_fields = getattr(model_class.PydanticMeta, "text_to_list")
            for field in text_to_list_fields:
                field_info = all_fields_info.get(field)[1]
                field_type = Union[List[str], str] if field_info.is_required() else Union[List[str], str, None]
                all_fields_info.update({field: (field_type, field_info)})
    else:
        include_fields.update(all_fields_info.keys())

    if extra_include:
        include_fields_dict = get_dict_from_pydanticmeta(model_class, extra_include)
        all_fields_info.update(include_fields_dict)
        include_fields.update(include_fields_dict.keys())
    if exclude:
        exclude_fields.update(set(exclude))
    if frozen_exclude:
        exclude_fields.update(set(frozen_exclude))

    all_fields = include_fields.difference(exclude_fields)
    try:
        if settings.app_settings.CREATE_EXCLUDE_ACTIVE_VALUE:
            try:
                all_fields.remove(settings.app_settings.WHETHER_DELETE_FIELD)
            except Exception:
                ...
        all_fields.remove(model_class._meta.pk_attr)
    except Exception:
        ...

    schema_name = name if name else model_class.__name__ + "CreateSchema"
    schema_field_dict = {field: all_fields_info[field] for field in all_fields}
    validators_dict = get_validate_dict_from_fields(schema_field_dict)
    field_validators = get_field_validate_dict(validate_field_info)
    text_to_list_validators_dict = get_model_validate_list_to_text(text_to_list_fields)
    schema: Type[T] = create_model(
        schema_name,
        **schema_field_dict,
        __config__=model_config,
        __validators__={**validators_dict, **field_validators, **text_to_list_validators_dict},
    )
    return schema


