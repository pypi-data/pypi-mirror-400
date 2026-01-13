from logging import warning
from typing import Type, Optional

from pydantic import BaseModel, create_model

from fastgenerateapi.pydantic_utils.base_model import model_config
from fastgenerateapi.controller.filter_controller import BaseFilter
from tortoise import Model

from fastgenerateapi.schemas_factory.common_function import get_validate_dict


def filter_schema_factory(model_class: Type[Model], fields: list[str, tuple[str, Type], BaseFilter] = None):
    """
        generate filter schema
    """
    model_fields = {}

    for base_field in fields or []:
        if not isinstance(base_field, BaseFilter):
            base_field = BaseFilter(base_field, model_class)
        f = base_field.model_field
        t = base_field.field_type
        if base_field.field_info:
            model_fields.update({
                f: (
                    Optional[t],
                    base_field.field_info
                )
            })
        else:
            warning(f"模型{model_class.__name__}筛选参数{base_field.model_field}未起效果")

    filter_params_model: Type[BaseModel] = create_model(
        model_class.__name__+"CommonFilterParams",
        **model_fields,
        __config__=model_config,
        __validators__=get_validate_dict(),
    )

    return filter_params_model



