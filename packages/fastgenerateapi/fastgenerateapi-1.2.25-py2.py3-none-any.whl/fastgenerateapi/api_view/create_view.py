import inspect
from typing import Optional, Type, Union, Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.types import DecoratedCallable
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from tortoise import Model
from tortoise.transactions import atomic

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.api_view.mixin.save_mixin import SaveMixin
from fastgenerateapi.data_type.data_type import DEPENDENCIES
from fastgenerateapi.data_type.tortoise_type import T_Model
from fastgenerateapi.schemas_factory import create_schema_factory, response_factory
from fastgenerateapi.settings.all_settings import settings


class CreateView(BaseView, SaveMixin):
    create_summary: Optional[str] = None
    create_route: Union[bool, DEPENDENCIES] = True
    create_schema: Optional[Type[BaseModel]] = None
    create_response_schema: Optional[Type[BaseModel]] = None
    """
    create_route: 创建路由开关，可以放依赖函数列表
    create_schema: 创建请求模型;
        优先级：  
            - create_schema：参数传入
            - create_schema_factory：数据库模型自动生成
                - 优选模型层[include, exclude, create_include, create_exclude](同时存在交集)
                - 无include和exclude默认模型层所有字段
    create_response_schema: 创建返回模型
    """

    @atomic()
    async def create(self, request_data, *args, **kwargs):
        try:
            data_dict = await self.set_create_fields(request_data=request_data, *args, **kwargs)
            data_dict = await self.set_save_fields(data_dict, request_data=request_data, *args, **kwargs)
            model = await self.set_create_model(data_dict, request_data=request_data, *args, **kwargs)
        except ValueError as e:
            error_field = str(e).split(" ")[0]
            if getattr(request_data, error_field):
                return self.error(msg=f"{self.get_field_description(self.model_class, error_field)}格式不正确")
            return self.error(msg=f"{self.get_field_description(self.model_class, error_field)}不能为空")

        await self.check_unique_field(data_dict, model_class=self.model_class)
        await model.save()

        await self.set_save_func(model, request_data, None, *args, **kwargs)

        return model

    async def set_create_fields(self, request_data, *args, **kwargs) -> dict:
        """
        添加属性:
            data_dict = request_data.dict(exclude_unset=True)
            data_dict.update({
                "user_id": request.user.id,
            })
            return data_dict
        """

        return request_data.dict(exclude_unset=True)

    async def set_create_model(self, data_dict: dict, request_data, *args, **kwargs) -> T_Model:
        """
        在数据模型校验前后修改值
        - 可用于全局修改
        添加属性:
        data_dict.update({
            "user_id": request.user.id,
        })
        """

        return self.model_class(**data_dict)

    def _create_decorator(self, *args: Any, **kwargs: Any) -> DecoratedCallable:
        async def route(
                request_data: self.create_schema,  # type: ignore
                request: Request,
                token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False)),
        ) -> JSONResponse:
            data = await self.create(
                request_data=request_data,
                request=request,
                token=token,
                *args,
                **kwargs
            )
            if isinstance(data, Model):
                if settings.app_settings.WHETHER_CREATE_RESPONSE_DATA:
                    if self.is_with_prefetch:
                        data = await self.get_object(data.id, self.model_class, self.is_with_prefetch)
                        await self.setattr_model(data, prefetch_related_fields=self.prefetch_related_fields)

                    return self.success(data=self.create_response_schema.model_validate(data))
                return self.success()
            if isinstance(data, JSONResponse):
                return data
            return self.success(data=data)

        return route

    def _handler_create_settings(self):
        if not self.create_route:
            return
        self.create_schema = self.create_schema or create_schema_factory(self.model_class)

        func_type = inspect.signature(self.create).return_annotation
        if func_type != inspect._empty and func_type is not None:
            self.create_response_schema = func_type
        if self.create_response_schema:
            self.create_response_schema_factory = response_factory(self.create_response_schema, name="Create")
        else:
            self.create_response_schema_factory = self.get_response_schema_factory()
            self.create_response_schema = self.response_schema
        if not self.create_summary:
            doc = self.create.__doc__
            self.create_summary = doc.strip().split("\n")[0] if doc else f"Create"
        path = f"/{settings.app_settings.ROUTER_CREATE_SUFFIX_FIELD}" if settings.app_settings.ROUTER_WHETHER_ADD_SUFFIX else ""
        self._add_api_route(
            path=path,
            endpoint=self._create_decorator(),
            methods=["POST"],
            response_model=self.create_response_schema_factory,  # type: ignore
            summary=self.create_summary,
            dependencies=self.create_route,
        )



