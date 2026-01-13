import importlib
from typing import List, Optional, Any

from pydantic import BaseModel as PydanticBaseModel, BaseConfig, Field, ConfigDict, field_validator, model_validator

from fastgenerateapi.pydantic_utils.json_encoders import JSON_ENCODERS
from fastgenerateapi.settings.all_settings import settings

alias_generator = None
try:
    if settings.app_settings.ALIAS_GENERATOR:
        if settings.app_settings.ALIAS_GENERATOR.__contains__(":"):
            module_path, class_name = settings.app_settings.ALIAS_GENERATOR.rsplit(':', maxsplit=1)
        elif settings.app_settings.ALIAS_GENERATOR.__contains__("."):
            module_path, class_name = settings.app_settings.ALIAS_GENERATOR.rsplit('.', maxsplit=1)
        else:
            module_path, class_name = "fastgenerateapi.utils", settings.app_settings.ALIAS_GENERATOR
        module = importlib.import_module(module_path)
        alias_generator = getattr(module, class_name)
except Exception:
    print(f"序列化参数命名方法路径【{settings.app_settings.ALIAS_GENERATOR}】错误，未生效！！！")
    alias_generator = None


class ModelConfig(ConfigDict):

    def __init__(self, seq=None, **kwargs):
        default_kwargs = {
            "json_encoders": JSON_ENCODERS,
            "extra": "ignore",  # v1 ignore v2 版本没有 Extra.ignore
            # orm_mode=True,  # v1 版本
            "from_attributes": True,  # v2 版本
            # "allow_population_by_field_name": True,  # v1 版本
            "populate_by_name": True,  # v2 版本,支持原本的属性和驼峰命名
            "alias_generator": alias_generator,
        }
        default_kwargs.update(kwargs)
        super().__init__(seq=seq, **default_kwargs)


model_config = ConfigDict(
    json_encoders=JSON_ENCODERS,
    extra="ignore",  # v1 ignore v2 版本没有 Extra.ignore
    # orm_mode=True,  # v1 版本
    from_attributes=True,  # v2 版本
    # allow_population_by_field_name=True,  # v1 版本
    populate_by_name=True,  # v2 版本,支持原本的属性和驼峰命名
    alias_generator=alias_generator,
)


# class Config(BaseConfig):
#     json_encoders = JSON_ENCODERS
#     extra = "ignore"  # v1 ignore v2 版本没有 Extra.ignore
#     orm_mode = True  # v1 版本
#     from_attributes = True  # v2 版本
#     allow_population_by_field_name = True  # v1 版本
#     populate_by_name = True  # v2 版本,支持原本的属性和驼峰命名
#     alias_generator = alias_generator


class BaseModel(PydanticBaseModel):
    model_config = model_config

    @field_validator('*', mode='before')  # '*' 表示匹配所有字段
    def empty_str_to_none(cls, v: Any) -> Any:
        """将空字符串转换为None，其他值保持不变"""
        if isinstance(v, str) and v.strip() == "":  # 处理纯空字符串或仅含空格的字符串
            return None
        return v


class PagePydantic(BaseModel):
    no_page: Optional[bool] = Field(
        default=False,
        alias=alias_generator(settings.app_settings.WHETHER_PAGE_FIELD) if alias_generator else settings.app_settings.WHETHER_PAGE_FIELD,
        description="是否分页"
    )
    page: Optional[int] = Field(
        default=1,
        alias=alias_generator(settings.app_settings.CURRENT_PAGE_FIELD) if alias_generator else settings.app_settings.CURRENT_PAGE_FIELD,
        description="当前页"
    )
    page_size: Optional[int] = Field(
        default=settings.app_settings.DEFAULT_PAGE_SIZE,
        alias=alias_generator(settings.app_settings.PAGE_SIZE_FIELD) if alias_generator else settings.app_settings.PAGE_SIZE_FIELD,
        description="每页数量"
    )

    @model_validator(mode='after')
    def func(cls, data):
        if data.page < 1:
            data.page = 1
        if not data.page_size or data.page_size < 1:
            data.page_size = settings.app_settings.DEFAULT_PAGE_SIZE
        if data.page_size > settings.app_settings.DEFAULT_MAX_PAGE_SIZE:
            data.page_size = settings.app_settings.DEFAULT_MAX_PAGE_SIZE
        return data


class EmptyPydantic(BaseModel):
    ...


class SearchPydantic(BaseModel):
    search: Optional[str] = Field(None, description="搜索")


class IdList(BaseModel):
    id_list: List[str] = Field([], description="id数组")


class IdResp(BaseModel):
    id: str = Field(..., description="主键")

