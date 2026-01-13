from typing import List, Any, Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.types import DecoratedCallable
from starlette.requests import Request
from starlette.responses import JSONResponse

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.utils.exception import NOT_FOUND


class SwitchView(BaseView):

    switch_route_fields: List[str] = None  # 布尔值|枚举值切换路由
    """
    # 生成一个路由： .../is_enabled/{pk}  方法：PUT
    # 无参数： 默认布尔值类型切换相反值    有参数：{"is_enabled":True} 切换参数值
    switch_route_fields = ["is_enabled", "status", ...]
    """

    async def switch(self, pk, request, filed, *args, **kwargs):
        try:
            request_data = await request.json()
        except Exception:
            request_data = {}

        model = await self.get_object(pk, self.model_class, is_with_prefetch=self.is_with_prefetch)
        setattr(
            model,
            filed,
            not getattr(model, filed) if request_data.get(filed) is None else request_data.get(filed)
        )
        await model.save()

        if self.is_with_prefetch:
            await self.setattr_model(model, prefetch_related_fields=self.prefetch_related_fields)

        return self.response_schema.model_dump(model)

    def _switch_decorator(self, filed, *args: Any, **kwargs: Any) -> DecoratedCallable:
        async def route(
                pk: str,
                request: Request,
                token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="token", auto_error=False)),
        ) -> JSONResponse:
            data = await self.switch(pk=pk, request=request, filed=filed, token=token, *args, **kwargs)
            if isinstance(data, JSONResponse):
                return data
            return self.success(data=data)
        return route

    def _handler_switch_route_settings(self):
        if not self.switch_route_fields:
            return

        for switch_route_field in self.switch_route_fields:
            if self.model_class._meta.fields_map.get(switch_route_field).field_type not in [bool, int]:
                self.error(msg=f"{switch_route_field} is not bool or int")
            self.switch_response_schema_factory = self.get_response_schema_factory()
            # 待增加数据库模型description的读取
            summary = f"Switch {switch_route_field}|切换{self.get_field_description(self.model_class, switch_route_field)}"
            self._add_api_route(
                path="/%s/{pk}" % ("switch_"+switch_route_field),
                endpoint=self._switch_decorator(switch_route_field),
                methods=["PUT"],
                response_model=self.switch_response_schema_factory,
                summary=summary,
                dependencies=True,
                error_responses=[NOT_FOUND],
            )


