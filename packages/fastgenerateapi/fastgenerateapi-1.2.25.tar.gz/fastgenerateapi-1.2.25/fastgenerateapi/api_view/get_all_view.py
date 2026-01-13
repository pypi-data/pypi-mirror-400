import inspect
from typing import Union, Optional, Type, cast, List, Any, Callable, Coroutine

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi.types import DecoratedCallable
from fastapi_cache import JsonCoder
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from starlette._utils import is_async_callable
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.api_view.mixin.get_mixin import GetMixin
from fastgenerateapi.cache.cache_decorator import get_all_cache_decorator
from fastgenerateapi.cache.key_builder import generate_key_builder
from fastgenerateapi.controller import SearchController, BaseFilter, FilterController
from fastgenerateapi.data_type.data_type import DEPENDENCIES, PYDANTIC_SCHEMA
from fastgenerateapi.data_type.tortoise_type import T_Model
from fastgenerateapi.deps import filter_params_deps
from fastgenerateapi.deps.filter_params_deps import search_params_deps, extra_filter_params_deps
from fastgenerateapi.pydantic_utils.base_model import PagePydantic
from fastgenerateapi.schemas_factory import get_all_schema_factory, get_page_schema_factory, response_factory
from fastgenerateapi.schemas_factory.get_all_schema_factory import get_list_schema_factory, hasattr_get_all_schema
from fastgenerateapi.settings.all_settings import settings


class GetAllView(BaseView, GetMixin):
    get_all_summary: Optional[str] = None
    get_all_route: Union[bool, DEPENDENCIES] = True
    get_all_schema: Optional[Type[PYDANTIC_SCHEMA]] = None
    search_fields: Union[None, list] = None
    filter_fields: Union[None, list] = None
    filter_schema: Optional[Type[PYDANTIC_SCHEMA]] = None
    extra_filter_schema: Optional[Type[PYDANTIC_SCHEMA]] = None
    order_by_fields: Union[None, list] = None
    auto_add_id_order: bool = True
    """
    get_all_route: 获取详情路由开关，可以放依赖函数列表
    get_all_schema: 返回序列化
        优先级：  
            - 1：get_all_schema:传入参数
            - 2：模型层get_all_include和get_all_exclude(同时存在交集)
            - 3：get_one_schemas
    search_fields: search搜索对应字段 
        example：("name__contains", str, "name") 类型是str的时候可以省略，没有第三个值时，自动双下划线转单下划线
    filter_fields: 筛选对应字段
        example： name__contains or (create_at__gt, datetime) or (create_at__gt, datetime, create_time)
    filter_schema: 筛选对应字段
        与filter_fields结果合并，存在相同值时，filter_schema覆盖filter_fields
    extra_filter_schema: 不用于筛选，可用于返回值判断
    order_by_fields: 排序对应字段
    auto_add_id_order: 是否自动在 order_by_fields 后面追加id排序
    """

    async def get_all(self, search: Optional[str], filters: dict, *args, **kwargs):
        queryset = await self.get_queryset(search=search, filters=filters, *args, **kwargs)

        return await self.get_page_data(
            queryset=queryset,
            prefetch_related_fields=self.prefetch_related_fields,
            *args, **kwargs
        )

    async def get_queryset(self, search: Optional[str], filters: dict, *args, **kwargs) -> QuerySet:
        """
        处理search搜索；处理筛选字段；处理外键预加载；处理排序
        """
        queryset = self.search_controller.query(queryset=self.queryset, value=search)
        queryset = await self.filter_queryset(queryset, filters, *args, **kwargs)
        queryset = self.filter_controller.query(queryset=queryset, values=filters)
        queryset = queryset.prefetch_related(*self.prefetch_related_fields.keys())
        if self.auto_add_id_order:
            self.order_by_fields = self.order_by_fields or []
            self.order_by_fields.append("id")
        if self.order_by_fields:
            queryset = queryset.order_by(*self.order_by_fields)

        return queryset

    async def filter_queryset(self, queryset: QuerySet, filters: dict, *args, **kwargs) -> QuerySet:
        """
        处理filters
            example： value = filters.pop(value, None)   queryset = queryset.filter(field=value+string)
        """
        return queryset

    async def set_get_all_model_list(self, model_list: List[T_Model], *args, **kwargs) -> List[T_Model]:
        """
        对于查询的model列表进行数据处理
        使用场景：
            存在每条数据重复请求时，如：model的id通过http请求获取相关信息，可此处统一请求
            储存在kwargs["extra_filters"]里，在set_get_all_model赋值
        使用示例：
            kwargs.setdefault("extra_filters", {})["_dict"] = {}
        """
        return model_list

    async def set_get_all_model(self, model: T_Model, *args, **kwargs) -> T_Model:
        """
        对于查询的model，展示数据处理
        """
        return model

    async def get_queryset_data(
            self,
            queryset: QuerySet,
            schema: Type[BaseModel] = None,
            paginator: Optional[PagePydantic] = PagePydantic(),
            model_handler: Optional[Callable] = None,
            model_handler_list: Optional[List[Callable]] = None,
            *args, **kwargs,
    ):
        """
        通用分页函数，获取对应的数据，和分页统计
        :param queryset:
        :param schema:
        :param paginator:
        :param model_handler:
        :param model_handler_list:
        :param args:
        :param kwargs:
        :return:
        """
        count = None
        if paginator.no_page:
            model_list = await queryset.all()
        else:
            count = await queryset.count()
            queryset = queryset.offset(cast(int, (paginator.page - 1) * paginator.page_size))
            model_list = await queryset.limit(paginator.page_size)

        if model_handler:
            if is_async_callable(model_handler):
                model_list = await model_handler(model_list, paginator=paginator, *args, **kwargs)
            else:
                model_list = model_handler(model_list, paginator=paginator, *args, **kwargs)
        if not schema:
            model_list = await self.set_get_all_model_list(model_list, paginator=paginator, *args, **kwargs)

        data_list = []
        for model in model_list:
            await self.setattr_model(model,*args, **kwargs)
            if model_handler_list:
                for i_model_handler in model_handler_list:
                    if is_async_callable(i_model_handler):
                        model = await i_model_handler(model, paginator=paginator,*args, **kwargs)
                    else:
                        model = i_model_handler(model, paginator=paginator,*args, **kwargs)
            if schema:
                data_list.append(schema.model_validate(model))
            else:
                model = await self.set_get_model(model, paginator=paginator,*args, **kwargs)
                model = await self.set_get_all_model(model, paginator=paginator, *args, **kwargs)
                data_list.append(self.get_all_schema.model_validate(model))

        return data_list, count

    def get_page_schema_func(self, data_list, count = None, schema: Type[BaseModel] = None, paginator: Optional[PagePydantic] = None, *args, **kwargs):
        """
        返回列表结果
        :param data_list:
        :param count:
        :param schema: 当使用自定义列表时使用，默认列表的get_all_schema
        :param paginator:
        :param args:
        :param kwargs: 自定义列表时，传schema或fields
        :return:
        """
        if paginator.no_page:
            page_schema = get_list_schema_factory(schema) if schema else self.get_all_list_schema
        else:
            page_schema = get_page_schema_factory(schema) if schema else self.get_all_page_schema

        return page_schema(
            **paginator.model_dump(by_alias=True),
            **{
                settings.app_settings.LIST_RESPONSE_FIELD: data_list,
                settings.app_settings.TOTAL_SIZE_FIELD: count,
            }
        )

    async def get_page_data(
        self,
        queryset: QuerySet,
        *args, **kwargs,
    ):
        """
        通用分页，获取序列化后的值
        :param queryset:
        :param args:
        :param kwargs: 其他参数 schema, paginator, prefetch_related_fields
        :return:
        """
        data_list, count = await self.get_queryset_data(queryset=queryset,*args, **kwargs)
        res = self.get_page_schema_func(data_list, count, *args, **kwargs)
        return res

    def _get_all_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        @get_all_cache_decorator(cache(expire=settings.app_settings.CACHE_GET_ALL_SECONDS, coder=JsonCoder,
                                       key_builder=generate_key_builder))
        async def route(
                request: Request,
                paginator: PagePydantic = Depends(),
                search: Optional[str] = Depends(search_params_deps(self.search_fields)),
                filters: dict = Depends(filter_params_deps(
                    model_class=self.model_class, fields=self.filter_fields, schema=self.filter_schema)),
                extra_filters: dict = Depends(extra_filter_params_deps(schema=self.extra_filter_schema)),
                token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False)),
        ) -> JSONResponse:
            data = await self.get_all(
                paginator=paginator,
                search=search,
                filters=filters,
                extra_filters=extra_filters,
                request=request,
                token=token,
                *args,
                **kwargs
            )
            if isinstance(data, JSONResponse):
                return data
            return self.success(data=data)

        return route

    def _handler_get_all_settings(self):
        if not self.get_all_route:
            return
        self.search_controller = SearchController(self.get_base_filter(self.search_fields, model_class=self.model_class))
        self.filter_controller = FilterController(self.get_base_filter(self.filter_fields, self.filter_schema, model_class=self.model_class))

        func_type = inspect.signature(self.get_all).return_annotation
        if func_type != inspect._empty and func_type is not None:
            self.get_all_schema = func_type
        if not self.get_all_schema:
            get_all_schema_include = []
            if self.prefetch_related_fields:
                get_all_schema_include = self._get_extra_related_schema()
            if hasattr_get_all_schema(self.model_class) or get_all_schema_include:
                self.get_all_schema = get_all_schema_factory(self.model_class, extra_include=get_all_schema_include)
            else:
                self.get_all_schema = self.get_response_schema()
        self.get_all_page_schema = get_page_schema_factory(self.get_all_schema)
        self.get_all_list_schema = get_list_schema_factory(self.get_all_schema)
        self.get_all_response_schema_factory = response_factory(self.get_all_page_schema, name="GetPage")
        if not self.get_all_summary:
            doc = self.get_all.__doc__
            self.get_all_summary = doc.strip().split("\n")[0] if doc else "Get All"
        path = f"/{settings.app_settings.ROUTER_GET_ALL_SUFFIX_FIELD}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
        self._add_api_route(
            path=path,
            endpoint=self._get_all_decorator(),
            methods=["GET"],
            response_model=self.get_all_response_schema_factory,
            summary=self.get_all_summary,
            dependencies=self.get_all_route,
        )
