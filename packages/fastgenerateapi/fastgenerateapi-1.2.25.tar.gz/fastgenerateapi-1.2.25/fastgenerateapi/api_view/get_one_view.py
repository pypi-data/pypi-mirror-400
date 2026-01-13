import inspect
from typing import Any, Union, Optional, Type

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.types import DecoratedCallable
from fastapi_cache import JsonCoder
from fastapi_cache.decorator import cache
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.api_view.mixin.get_mixin import GetMixin
from fastgenerateapi.cache.cache_decorator import get_one_cache_decorator
from fastgenerateapi.cache.key_builder import generate_key_builder
from fastgenerateapi.data_type.data_type import CALLABLE, DEPENDENCIES
from fastgenerateapi.data_type.tortoise_type import T_Model
from fastgenerateapi.schemas_factory import response_factory
from fastgenerateapi.settings.all_settings import settings
from fastgenerateapi.utils.exception import NOT_FOUND


class GetOneView(BaseView, GetMixin):
    get_one_summary: Optional[str] = None
    get_one_route: Union[bool, DEPENDENCIES] = True
    get_one_schema: Optional[Type[BaseModel]] = None
    """
    get_one_route: 获取详情路由开关，可以放依赖函数列表
    get_one_schema: 返回序列化
        优先级：  
            - get_one_schema：参数传入
            - get_one_schema_factory：数据库模型自动生成
                - 优选模型层get_one_include和get_one_exclude(同时存在交集)
                - 合并模型层include和exclude(同时存在交集)
                - 模型层所有字段

    prefetch_related_fields：额外展示字段
    is_with_prefetch: 是否带有列表的prefetch_related_fields
    """

    async def get_one(self, pk: str, *args, **kwargs):
        model = await self.get_object(pk, self.model_class, is_with_prefetch=self.is_with_prefetch)
        if self.is_with_prefetch:
            await self.setattr_model(model, prefetch_related_fields=self.prefetch_related_fields, *args, **kwargs)

        model = await self.set_get_model(model, *args, **kwargs)
        model = await self.set_get_one_model(model, *args, **kwargs)

        return self.get_one_schema.model_validate(model)

    async def set_get_one_model(self, model: T_Model, *args, **kwargs) -> T_Model:
        """
        对于查询的model，展示数据处理
        """
        return model

    def _get_one_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        @get_one_cache_decorator(cache(expire=settings.app_settings.CACHE_GET_ONE_SECONDS, coder=JsonCoder, key_builder=generate_key_builder))
        async def route(
                pk: str,
                request: Request,
                token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False)),
        ) -> JSONResponse:
            data = await self.get_one(
                pk=pk,
                request=request,
                token=token,
                *args, **kwargs
            )
            if isinstance(data, JSONResponse):
                return data
            return self.success(data=data)
        return route

    def _handler_get_one_settings(self):
        if not self.get_one_route:
            return

        func_type = inspect.signature(self.get_one).return_annotation
        if func_type != inspect._empty and func_type is not None:
            self.get_one_schema = func_type
        if not self.get_one_schema:
            self.get_one_schema = self.get_response_schema()

        self.get_one_response_schema_factory = response_factory(self.get_one_schema, name="GetOne")
        if not self.get_one_summary:
            doc = self.get_one.__doc__
            self.get_one_summary = doc.strip().split("\n")[0] if self.get_one.__doc__ else "Get One"
        path = f"/{settings.app_settings.ROUTER_GET_ONE_SUFFIX_FIELD}/{'{pk}'}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else "/{pk}"
        self._add_api_route(
            path=path,
            endpoint=self._get_one_decorator(),
            methods=["GET"],
            response_model=self.get_one_response_schema_factory,
            summary=self.get_one_summary,
            dependencies=self.get_one_route,
            error_responses=[NOT_FOUND],
        )










