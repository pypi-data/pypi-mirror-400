import time
import uuid
from copy import copy
from typing import Optional, Type, List, Union, Sequence, Dict, Any
from urllib.parse import parse_qs

from fastapi import params
from pydantic._internal._model_construction import ModelMetaclass
from tortoise.queryset import QuerySet

from pydantic import create_model, BaseModel
from starlette.requests import Request
from tortoise import Model

from fastgenerateapi.api_view.mixin.base_mixin import BaseMixin
from fastgenerateapi.api_view.mixin.dbmodel_mixin import DBModelMixin
from fastgenerateapi.api_view.mixin.response_mixin import ResponseMixin
from fastgenerateapi.api_view.mixin.tool_mixin import ToolMixin
from fastgenerateapi.data_type.tortoise_type import T_Model
from fastgenerateapi.schemas_factory import get_one_schema_factory, response_factory
from fastgenerateapi.settings.all_settings import settings
from fastgenerateapi.utils.exception import NOT_FOUND


class BaseView(BaseMixin, ResponseMixin, ToolMixin, DBModelMixin):

    prefix: Optional[str] = None  # 路由追加后缀
    model_class: Optional[Type[T_Model]] = None  # 数据库模型
    prefetch_related_fields: Optional[dict] = None
    is_with_prefetch: Optional[bool] = False
    response_schema: Optional[Type[BaseModel]] = None  # 通用返回序列化
    dependencies: Optional[Sequence[params.Depends]] = None
    tags: Optional[List[str]] = None  # swagger标签
    check_ignore_error_fields: Optional[List[str]] = None # 检查唯一字段报错时，不展示这个字段

    """
    # 增加外键字段显示
    prefetch_related_fields = {
          "avatar": None,           # 外键内容对应字典的形式
          "avatar": ["id", ("url", "avatar_url")]   # 增加 avatar_id,avatar_url2个字段
    }
    is_with_prefetch: 是否带有列表的prefetch_related_fields
    """

    @property
    def queryset(self) -> QuerySet:
        if not self.model_class:
            return self.error(msg="model_class not allow None")

        return self.get_active_queryset(self.model_class)

    @staticmethod
    def get_active_queryset(model_class: Union[Type[Model], QuerySet, None] = None) -> QuerySet:
        if not model_class:
            raise ResponseMixin.error(f"model_class not allow None")
        delete_filter_dict = {settings.app_settings.WHETHER_DELETE_FIELD: True}
        if settings.app_settings.DELETE_FIELD_TYPE == "time":
            delete_filter_dict = {settings.app_settings.WHETHER_DELETE_FIELD: 0}
        queryset = model_class.filter(**delete_filter_dict)

        return queryset

    @property
    def relation_queryset(self) -> QuerySet:
        if not self.relation_model_class:
            return self.error(msg="relation_model_class not allow None")
        return self.get_active_queryset(self.relation_model_class)

    @classmethod
    async def get_object(cls, pk, model_class: Type[T_Model], is_with_prefetch=False) -> T_Model:
        queryset = cls.get_active_queryset(model_class).filter(id=pk)
        if is_with_prefetch:
            queryset = queryset.prefetch_related(*cls.prefetch_related_fields.keys())
        model = await queryset.first()
        if model:
            return model
        else:
            raise NOT_FOUND

    @staticmethod
    def _delete_value():
        result = False
        if settings.app_settings.DELETE_FIELD_TYPE == "time":
            result = int(time.time() * 1000)
        return result

    @staticmethod
    async def delete_queryset(queryset: QuerySet):
        """
        考虑到不一定会集成已有的模型，删除根据是否存在字段来判断
        :param queryset:
        :return:
        """
        if settings.app_settings.WHETHER_DELETE_FIELD in queryset.fields:
            await queryset.update(**{
                settings.app_settings.WHETHER_DELETE_FIELD: BaseView._delete_value()
            })
        else:
            await queryset.delete()

    @staticmethod
    async def setattr_model(model: Model, prefetch_related_fields, *args, **kwargs) -> Model:
        if not prefetch_related_fields:
            return model
        for key, value_list in prefetch_related_fields.items():
            if value_list is None or isinstance(value_list, ModelMetaclass):
                continue
            if isinstance(value_list, str):
                value_list = [value_list]
            key_list = key.split("__")
            attr_model = copy(model)
            for attr_key in key_list:
                attr_model = getattr(attr_model, attr_key, None)

            if attr_model:
                if settings.app_settings.SCHEMAS_UNDERLINE_WHETHER_DOUBLE_TO_SINGLE:
                    key = key.replace("__", "_")
                for value in value_list:
                    if type(value) == str:
                        setattr(model, key + "_" + value, getattr(attr_model, value, None))
                    elif type(value) == tuple and len(value) == 2:
                        setattr(model, value[1], getattr(attr_model, value[0], None))
        return model

    @staticmethod
    async def getattr_model(model: Model, fields: List[Union[str, tuple]]) -> BaseModel:
        model_dict = {}
        model_fields = {}
        for field in fields:
            if type(field) == str:
                key_list = field.split("__")
                attr_model = copy(model)
                for attr_key in key_list:
                    attr_model = getattr(attr_model, attr_key, None)
                model_dict[field] = attr_model
                model_fields[field] = (type(attr_model), ...)
            if type(field) == tuple and len(field) == 2:
                key_list = field[0].split("__")
                attr_model = copy(model)
                for attr_key in key_list:
                    attr_model = getattr(attr_model, attr_key, None)
                model_dict[field[1]] = attr_model
                model_fields[field[1]] = (type(attr_model), ...)
        schema = create_model(
            f"{Model.__name__}{uuid.uuid4()}",
            **model_fields
        )
        return schema.model_validate(model_dict)

    async def check_unique_field(
            self,
            data_dict: dict,
            model_class: Type[Model],
            model: Union[Model, None] = None,
            check_ignore_error_fields: List[str] = None,
            error_format: Optional[str] = None,
            error_value_list: Optional[List[str]] = None,
    ):
        """
        校验模型中设置了 唯一索引和联合唯一索引 的字段
        :param data_dict: 修改或创建的数据字典
        :param model_class: 数据库模型
        :param model: 修改前的数据，用于判断是否修改了字段，当唯一字段与数据data_dict一致时，不会做校验
        :param check_ignore_error_fields: 错误提示忽略字段，会合并类上的字段
        :param error_format: 错误格式，例如： "错误：输入年龄 '{}' 无效！合法范围是 {}-{} 岁"
        :param error_value_list: 错误字段列表 ，例如：[input_age, min_age, max_age]
        :return:
        """
        check_unique_fields = self._get_unique_fields(model_class)
        check_unique_together_fields = self._get_unique_together_fields(model_class)
        for unique_field in check_unique_fields:
            if unique_field in data_dict:
                unique_field_value = data_dict.get(unique_field)
                if model and unique_field_value == getattr(model, unique_field):
                    continue
                if await model_class.filter(**{unique_field: unique_field_value}).first():
                    return self.error(msg=f"{self.get_field_description(model_class, unique_field)}已存在相同值：{unique_field_value}")
        # 聚合忽略错误提示字段
        ignore_error_field_list = check_ignore_error_fields or []
        if settings.app_settings.CHECK_IGNORE_ERROR_FIELDS:
            ignore_error_field_list.extend(settings.app_settings.CHECK_IGNORE_ERROR_FIELDS.split(","))
        if self.check_ignore_error_fields:
            ignore_error_field_list.extend(self.check_ignore_error_fields)
        for unique_together_fields in check_unique_together_fields:
            filter_fields = {}
            is_equal = True
            description_fields = []
            for unique_together_field in unique_together_fields:
                has_unique_together_field = unique_together_field in data_dict
                unique_together_field_value = data_dict.get(unique_together_field)
                if model:
                    if has_unique_together_field:
                        filter_fields[unique_together_field] = unique_together_field_value
                        if unique_together_field_value != getattr(model, unique_together_field):
                            is_equal = False
                            description_fields.append(unique_together_field)
                    else:
                        filter_fields[unique_together_field] = getattr(model, unique_together_field)
                else:
                    if has_unique_together_field:
                        is_equal = False
                        description_fields.append(unique_together_field)
                        filter_fields[unique_together_field] = unique_together_field_value
                    elif unique_together_field == settings.app_settings.WHETHER_DELETE_FIELD:
                        if settings.app_settings.DELETE_FIELD_TYPE  == "time":
                            filter_fields[unique_together_field] = 0
                        else:
                            filter_fields[unique_together_field] = True
            if is_equal:
                continue

            if await model_class.filter(**filter_fields).first():
                if error_format and error_value_list:
                    return self.error(
                        status_code=422,
                        msg=error_format.format(*[data_dict[k] for k in error_value_list])
                    )
                if settings.app_settings.WHETHER_DELETE_FIELD in description_fields:
                    description_fields.remove(settings.app_settings.WHETHER_DELETE_FIELD)
                for ignore_error_field in ignore_error_field_list:
                    if ignore_error_field in description_fields:
                        description_fields.remove(ignore_error_field)
                return self.error(
                    status_code=422,
                    msg=f"{self.get_field_description(model_class, description_fields)}已存在相同值：{[filter_fields.get(field) for field in description_fields]}"
                )

    @staticmethod
    async def get_params(request: Request) -> dict:
        result = {}
        data = parse_qs(str(request.query_params), keep_blank_values=False)
        for key, val in data.items():
            result[key] = val[0]
        return result

    def _get_extra_related_schema(self):
        """
        prefetch_related_fields 转换为 extra_include 的参数
        :return:
        """
        schema_include = []
        for key, value in self.prefetch_related_fields.items():
            if not value:
                continue
            if isinstance(value, ModelMetaclass):
                schema_include.append((key, Optional[value]))
            elif type(value) in [list, tuple, set]:
                for val in value:
                    val_str = val
                    if type(val) in [list, tuple, set]:
                        val_str = val[0]
                    schema_include.append(key + "__" + val_str)
        return schema_include

    def get_response_schema(self):
        """
        如果response_schema不存在，则生成
        :return:
        """
        if not self.response_schema:
            get_one_schema_include = []
            if self.is_with_prefetch and self.prefetch_related_fields:
                get_one_schema_include = self._get_extra_related_schema()
            self.response_schema = get_one_schema_factory(self.model_class, extra_include=get_one_schema_include)

        return self.response_schema

    def get_response_schema_factory(self):
        """
        如果response_schema不存在，则生成
        :return:
        """
        self.get_response_schema()
        self.response_schema_factory = response_factory(self.response_schema, name="Common")

        return self.response_schema_factory



