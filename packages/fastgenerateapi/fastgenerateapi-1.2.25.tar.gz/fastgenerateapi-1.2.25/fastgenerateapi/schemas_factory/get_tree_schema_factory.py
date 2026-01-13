from typing import Type, Optional, Union, List

from pydantic.fields import FieldInfo
from tortoise import Model
from pydantic import create_model

from fastgenerateapi.data_type.data_type import T
from fastgenerateapi.pydantic_utils.base_model import model_config
from fastgenerateapi.schemas_factory.common_function import get_dict_from_model_fields, get_dict_from_pydanticmeta, \
    get_model_validate_text_to_list
from fastgenerateapi.settings.all_settings import settings


def get_tree_schema_factory(
        model_class: Type[Model],
        include: Union[list, tuple, set] = None,
        extra_include: Union[list, tuple, set] = None,
        exclude: Union[list, tuple, set] = None,
        pydantic_meta: Optional[bool] = True,
        pydantic_meta_include: Union[list, tuple, set] = None,
        pydantic_meta_exclude: Optional[bool] = True,
        pydantic_meta_get_include: Optional[bool] = True,
        pydantic_meta_get_exclude: Optional[bool] = True,
        pydantic_meta_get_tree_include: Optional[bool] = True,
        pydantic_meta_get_tree_exclude: Optional[bool] = True,
        pydantic_meta_text_to_list: Optional[bool] = True,
        name: Optional[str] = None
) -> Optional[Type[T]]:
    """
    Is used to create a GetTreeSchema
    """
    all_fields_info: dict = get_dict_from_model_fields(model_class)

    include_fields = set()
    exclude_fields = set()
    text_to_list_fields = set()
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

        if pydantic_meta_get_include and hasattr(model_class.PydanticMeta, "get_include"):
            get_include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.get_include)
            all_fields_info.update(get_include_fields_dict)
            include_fields.update(get_include_fields_dict.keys())
        if pydantic_meta_get_exclude and hasattr(model_class.PydanticMeta, "get_exclude"):
            exclude_fields.update(model_class.PydanticMeta.get_exclude)

        if pydantic_meta_get_tree_include and hasattr(model_class.PydanticMeta, "get_tree_include"):
            get_tree_include_fields_dict = get_dict_from_pydanticmeta(model_class, model_class.PydanticMeta.get_tree_include)
            all_fields_info.update(get_tree_include_fields_dict)
            include_fields.update(get_tree_include_fields_dict.keys())
        if pydantic_meta_get_tree_exclude and hasattr(model_class.PydanticMeta, "get_tree_exclude"):
            exclude_fields.update(model_class.PydanticMeta.get_tree_exclude)
        if pydantic_meta_text_to_list and hasattr(model_class.PydanticMeta, "text_to_list"):
            text_to_list_fields = getattr(model_class.PydanticMeta, "text_to_list")
            for field in text_to_list_fields:
                field_info = all_fields_info.get(field)[1]
                field_type = List[str] if field_info.is_required() else Optional[List[str]]
                all_fields_info.update({field: (field_type, field_info)})
    else:
        include_fields.update(all_fields_info.keys())

    if extra_include:
        include_fields_dict = get_dict_from_pydanticmeta(model_class, extra_include)
        all_fields_info.update(include_fields_dict)
        include_fields.update(include_fields_dict.keys())
    if exclude:
        exclude_fields.update(exclude)

    all_fields = include_fields.difference(exclude_fields)
    all_fields.add(settings.app_settings.DEFAULT_TREE_CHILDREN_FIELD)
    if settings.app_settings.GET_EXCLUDE_ACTIVE_VALUE:
        try:
            all_fields.remove(settings.app_settings.WHETHER_DELETE_FIELD)
        except Exception:
            ...
    schema_name = name if name else model_class.__name__ + "GetTreeSchema"

    all_fields_info.setdefault(
        settings.app_settings.DEFAULT_TREE_CHILDREN_FIELD,
        (Optional[List[schema_name]], FieldInfo(default=[], description="子级目录"))
    )

    text_to_list_validators_dict = get_model_validate_text_to_list(text_to_list_fields)
    schema: Type[T] = create_model(
        schema_name,
        **{field: all_fields_info[field] for field in all_fields},
        __config__=model_config,
        __validators__={**text_to_list_validators_dict},
    )

    return schema




