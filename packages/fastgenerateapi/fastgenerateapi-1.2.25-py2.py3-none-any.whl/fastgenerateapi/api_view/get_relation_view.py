import inspect
from typing import Union, Optional, Type, cast, List, Any

from fastapi import Depends, Query
from fastapi.security import OAuth2PasswordBearer
from fastapi.types import DecoratedCallable
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise import Model
from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.controller import SearchController, BaseFilter, FilterController
from fastgenerateapi.data_type.data_type import DEPENDENCIES
from fastgenerateapi.data_type.tortoise_type import T_Model
from fastgenerateapi.deps import filter_params_deps
from fastgenerateapi.deps.filter_params_deps import search_params_deps
from fastgenerateapi.pydantic_utils.base_model import PagePydantic
from fastgenerateapi.schemas_factory import get_page_schema_factory, response_factory
from fastgenerateapi.schemas_factory.get_all_schema_factory import get_list_schema_factory
from fastgenerateapi.schemas_factory.get_relation_schema_factory import get_relation_schema_factory
from fastgenerateapi.settings.all_settings import settings


class GetRelationView(BaseView):
    path_id_name: str
    relation_id_name: str
    relation_model_class: Optional[Type[Model]]
    get_relation_summary: Optional[str] = None
    get_relation_route: Union[bool, DEPENDENCIES] = True
    get_relation_schema: Optional[Type[BaseModel]] = None
    search_fields: Union[None, list] = None
    filter_fields: Union[None, list] = None
    relation_filter_fields: Union[None, list] = None
    order_by_fields: Union[None, list] = None
    relation_order_by_fields: Union[None, list] = None
    """
    path_id_name: 路径id在模型中对应的字段名
    relation_id_name: 模型中需要修改的字段名
    model_class： 查询数据的模型
    relation_model_class： 多对多数据库模型

    get_relation_route: 获取详情路由开关，可以放依赖函数列表
    get_relation_schema: 返回序列化
        优先级：
            - 传入参数
            - 模型层get_relation_include和get_relation_exclude(同时存在交集)
            - get_one_schemas
    search_fields: search搜索对应字段
        example：("name__contains", str, "name") 类型是str的时候可以省略，没有第三个值时，自动双下划线转单下划线
    filter_fields: 筛选对应字段
        example： name__contains or (create_at__gt, datetime) or (create_at__gt, datetime, create_time)
    relation_filter_fields： 多对多关联表筛选对应字段
    order_by_fields: 排序对应字段
    relation_order_by_fields: 多对多关联表排序对应字段
    """

    async def get_relation(self, pk: str, search: Optional[str], filters: dict, relation_filters: dict, *args, **kwargs):
        relation_queryset = await self.get_relation_queryset(filters=relation_filters, *args, **kwargs)
        id_list = relation_queryset.filter(Q(**{self.path_id_name: pk})).values_list(self.relation_id_name, flat=True)

        queryset = await self.get_queryset(search=search, filters=filters, *args, **kwargs)

        return await self.get_tree_data(queryset=queryset, id_list=id_list, *args, **kwargs)

    async def get_relation_queryset(self, filters: dict, *args, **kwargs) -> QuerySet:
        """
        处理筛选字段；处理排序
        """
        queryset = self.relation_filter_queryset(self.relation_queryset, filters)
        queryset = await self.filter_relation_controller.query(queryset=queryset, values=filters)
        if self.relation_order_by_fields:
            queryset = queryset.order_by(*self.relation_order_by_fields)

        return queryset

    async def get_queryset(self, search: str, filters: dict, *args, **kwargs) -> QuerySet:
        """
        处理search搜索；处理筛选字段；处理外键预加载；处理排序
        """
        queryset = self.search_controller.query(queryset=self.queryset, value=search)
        queryset = await self.filter_queryset(queryset, filters)
        queryset = self.filter_controller.query(queryset=queryset, values=filters)
        queryset = queryset.prefetch_related(*self.prefetch_related_fields.keys()).order_by(*self.order_by_fields or [])

        return queryset

    async def relation_filter_queryset(self, queryset: QuerySet, filters: dict) -> QuerySet:
        """
        处理filters
            example： value = filters.pop(value, None)   queryset = queryset.filter(field=value+string)
        """
        return queryset

    async def filter_queryset(self, queryset: QuerySet, filters: dict) -> QuerySet:
        """
        处理filters
            example： value = filters.pop(value, None)   queryset = queryset.filter(field=value+string)
        """
        return queryset

    async def set_get_relation_model(self, model: T_Model) -> T_Model:
        """
        对于查询的model，展示数据处理
        """
        return model

    async def get_tree_data(
            self,
            queryset: QuerySet,
            id_list,
            paginator: Optional[PagePydantic] = PagePydantic(),
            fields: List[Union[str, tuple]] = None,
            *args, **kwargs
    ) -> Union[dict, str, None, BaseModel]:

        data_list = []
        if paginator.no_page:
            model_list = await queryset.filter(id__in=id_list).all()
        else:
            if self.relation_order_by_fields:
                id_list = id_list[cast(int, (paginator.page - 1) * paginator.page_size): paginator.page_size]
            queryset = queryset.filter(id__in=id_list)
            count = await queryset.count()
            if self.relation_order_by_fields:
                model_list = await queryset
            else:
                queryset = queryset.offset(cast(int, (paginator.page - 1) * paginator.page_size))
                model_list = await queryset.limit(paginator.page_size)

        for model in model_list:
            await self.setattr_model(model, prefetch_related_fields=self.prefetch_related_fields, *args, **kwargs)
            await self.set_get_relation_model(model)
            data_list.append(self.get_relation_schema.model_validate(model))

        if paginator.no_page:
            return self.get_relation_list_schema(**{
                settings.app_settings.LIST_RESPONSE_FIELD: data_list,
            })
        return self.get_relation_page_schema(
            **paginator.model_dump(by_alias=True),
            **{
                settings.app_settings.TOTAL_SIZE_FIELD: count,
                settings.app_settings.LIST_RESPONSE_FIELD: data_list,
            }
        )

    def _get_relation_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        async def route(
                pk: str,
                request: Request,
                paginator: PagePydantic = Depends(),
                search: Optional[str] = Depends(search_params_deps(self.search_fields)),
                filters: dict = Depends(filter_params_deps(model_class=self.model_class, fields=self.filter_fields)),
                relation_filters: dict = Depends(
                    filter_params_deps(model_class=self.relation_model_class, fields=self.relation_filter_fields)),
                token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False)),
        ) -> JSONResponse:
            data = await self.get_relation(
                pk=pk,
                paginator=paginator,
                search=search,
                filters=filters,
                relation_filters=relation_filters,
                request=request,
                token=token,
                *args,
                **kwargs
            )
            if isinstance(data, JSONResponse):
                return data
            return self.success(data=data)
        return route

    def _handler_get_relation_settings(self):
        if not self.get_relation_route:
            return
        self.search_controller = SearchController(self.get_base_filter(self.search_fields, model_class=self.model_class))
        self.filter_controller = FilterController(self.get_base_filter(self.filter_fields, model_class=self.model_class))
        self.filter_relation_controller = FilterController(self.get_base_filter(self.relation_filter_fields, model_class=self.model_class))

        func_type = inspect.signature(self.get_relation).return_annotation
        if func_type != inspect._empty and func_type is not None:
            self.get_relation_schema = func_type
        self.get_relation_schema = self.get_relation_schema or get_relation_schema_factory(self.model_class)
        self.get_relation_page_schema = get_page_schema_factory(self.get_relation_schema)
        self.get_relation_list_schema = get_list_schema_factory(self.get_relation_schema)
        self.get_relation_response_schema_factory = response_factory(self.get_relation_page_schema, name="GetPage")
        if not self.get_relation_summary:
            doc = self.get_relation.__doc__
            summary = doc.strip().split("\n")[0] if doc else f"Get {self.model_class.__name__.title()}"
        path = f"/get-{self.relation_id_name.removesuffix('_id')}-by-{self.path_id_name.removesuffix('_id')}/{'{pk}'}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
        self._add_api_route(
            path=path,
            endpoint=self._get_relation_decorator(),
            methods=["GET"],
            response_model=self.get_relation_response_schema_factory,
            summary=self.get_relation_summary,
            dependencies=self.get_relation_route,
        )



