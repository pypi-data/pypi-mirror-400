import inspect
from typing import Optional, Type, Any, Union

from fastapi import Query, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.types import DecoratedCallable
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.transactions import atomic

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.data_type.data_type import CALLABLE, DEPENDENCIES
from fastgenerateapi.deps.filter_params_deps import filter_json_deps
from fastgenerateapi.pydantic_utils.base_model import IdList, SearchPydantic
from fastgenerateapi.schemas_factory import response_factory
from fastgenerateapi.settings.all_settings import settings


class DeleteFilterView(BaseView):
    delete_filter_summary: Optional[str] = None
    delete_filter_route: Union[bool, DEPENDENCIES] = True
    delete_filter_response_schema: Optional[Type[BaseModel]] = None
    """
    必须继承 GetAllView 才能使用
    与 GetAllView 同步的筛选条件
    delete_filter_route: 删除路由开关，可以放依赖函数列表
    delete_filter_response_schema: 删除返回模型
    """

    @atomic()
    async def destroy_filter(self, search: str, request_data, filters: dict, *args, **kwargs):
        queryset = await self.get_queryset(search=search, filters=filters, *args, **kwargs)
        queryset = await self.get_del_filter_queryset(queryset, request_data=request_data, *args, **kwargs)
        await self.delete_queryset(queryset)

        return

    async def get_del_filter_queryset(self, queryset, request_data, *args, **kwargs):
        queryset = queryset.filter(id__in=request_data.id_list)
        return queryset

    def _delete_filter_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        async def route(
                request: Request,
                search: SearchPydantic,
                request_data: IdList,
                filters: dict = Depends(filter_json_deps(model_class=self.model_class, fields=self.filter_fields)),
                token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False)),
        ) -> JSONResponse:
            data = await self.destroy_filter(
                search=search.search,
                request_data=request_data,
                filters=filters,
                request=request,
                token=token,
                *args, **kwargs
            )
            if isinstance(data, JSONResponse):
                return data
            return self.success(msg="删除成功", data=data)
        return route

    def _handler_destroy_filter_settings(self):
        if self.delete_filter_route:
            return

        self.delete_filter_response_schema_factory = None
        func_type = inspect.signature(self.destroy_filter).return_annotation
        if func_type != inspect._empty and func_type is not None:
            self.delete_filter_response_schema = func_type
        if self.delete_filter_response_schema:
            self.delete_filter_response_schema_factory = response_factory(self.delete_filter_response_schema, name="DeleteFilter")
        if not self.delete_filter_summary:
            doc = self.destroy_filter.__doc__
            self.delete_filter_summary = doc.strip().split("\n")[0] if doc else "Delete Filter"
        path = f"/{settings.app_settings.ROUTER_FILTER_DELETE_SUFFIX_FIELD}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
        self._add_api_route(
            path=path,
            endpoint=self._delete_filter_decorator(),
            methods=["DELETE"],
            response_model=self.delete_filter_response_schema_factory,
            summary=self.delete_filter_summary,
            dependencies=self.delete_filter_route,
        )





