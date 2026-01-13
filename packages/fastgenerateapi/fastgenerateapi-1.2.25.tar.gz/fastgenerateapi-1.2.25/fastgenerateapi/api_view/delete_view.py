import inspect
import time
from typing import Optional, Type, Any, Union

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.types import DecoratedCallable
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise.transactions import atomic

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.data_type.data_type import CALLABLE, DEPENDENCIES
from fastgenerateapi.pydantic_utils.base_model import IdList
from fastgenerateapi.schemas_factory import response_factory, get_one_schema_factory
from fastgenerateapi.settings.all_settings import settings


class DeleteView(BaseView):
    delete_summary: Optional[str] = None
    delete_route: Union[bool, DEPENDENCIES] = True
    delete_schema: Optional[Type[BaseModel]] = IdList
    delete_response_schema: Optional[Type[BaseModel]] = IdList
    """
    delete_route: 删除路由开关，可以放依赖函数列表
    delete_schema: 删除请求模型
    delete_response_schema: 删除返回模型
    """

    @atomic()
    async def destroy(self, request_data, *args, **kwargs):
        queryset = await self.get_del_queryset(request_data=request_data, *args, **kwargs)
        await self.delete_queryset(queryset)
        await self.set_destroy(request_data, *args, **kwargs)

        return

    async def get_del_queryset(self, request_data, *args, **kwargs):
        queryset = self.queryset.filter(id__in=request_data.id_list)
        return queryset

    async def set_destroy(self, request_data, *args, **kwargs):
        return

    def _delete_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        async def route(
                request_data: self.delete_schema,  # type: ignore
                request: Request,
                token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False)),
        ) -> JSONResponse:
            data = await self.destroy(
                request_data=request_data,
                request=request,
                token=token,
                *args, **kwargs
            )

            if isinstance(data, JSONResponse):
                return data
            return self.success(msg="删除成功", data=data)
        return route

    def _handler_delete_settings(self):
        if not self.delete_route:
            return

        self.delete_response_schema_factory = None
        func_type = inspect.signature(self.destroy).return_annotation
        if func_type != inspect._empty and func_type is not None:
            self.delete_response_schema = func_type
        if self.delete_response_schema:
            self.delete_response_schema_factory = response_factory(self.delete_response_schema, name="Delete")
        if not self.delete_summary:
            doc = self.destroy.__doc__
            self.delete_summary = doc.strip().split("\n")[0] if doc else "Delete"
        path = f"/{settings.app_settings.ROUTER_DELETE_SUFFIX_FIELD}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
        self._add_api_route(
            path=path,
            endpoint=self._delete_decorator(),
            methods=["DELETE"],
            response_model=self.delete_response_schema_factory,
            summary=self.delete_summary,
            dependencies=self.delete_route,
        )





