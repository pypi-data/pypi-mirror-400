import inspect

from fastgenerateapi.settings.all_settings import settings
from pydantic import BaseModel

from fastgenerateapi.api_view.mixin.response_mixin import ResponseMixin
from fastgenerateapi.data_type.data_type import DEPENDENCIES
from fastgenerateapi.schemas_factory import response_factory


class BaseRouter(ResponseMixin):
    def __init__(
            self,
            router_class,
            func_name: str,
            func_type=None,
            method: str = "POST",
            prefix: str = None,
            dependencies: DEPENDENCIES = None,
            summary: str = None,
    ):
        self.func_name = func_name
        if method.upper() in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            self.method = method.upper()
        else:
            self.error(msg=f"方法 {func_name} 中 {method} 不符合规范")

        self.prefix = prefix
        if not summary:
            doc = getattr(router_class, func_name).__doc__
            summary = doc.strip().split("\n")[0] if doc else func_name.lstrip("view_").rstrip("_pk").replace(
                "_"," ").title()
        self.summary = summary

        if func_type != inspect._empty and func_type is not None:
            self.response_model = response_factory(func_type)
        else:
            self.response_model = None
        self.dependencies = dependencies



class RouterController:

    def __init__(self, router_class, func_name_return_type_tuple_list):
        self.router_data = []
        for func_name, func_type in func_name_return_type_tuple_list:
            route_info_list = func_name.split("__")
            if route_info_list[-1] in ["pk", "id"]:
                route_info_list[-1] = "{" + route_info_list[-1] + "}"
            route_name = "/".join(route_info_list)
            route_info_list = route_name.split("_")
            method = route_info_list[1].upper()
            middle_list = route_info_list[2:]
            if settings.app_settings.ROUTER_WHETHER_UNDERLINE_TO_STRIKE:
                middle_field = "-".join(middle_list)
            else:
                middle_field = "_".join(middle_list)
            if method == "GET":
                prefix_field = settings.app_settings.RESTFUL_GET_ROUTER_ADD_PREFIX or ""
                suffix_field = settings.app_settings.RESTFUL_GET_ROUTER_ADD_SUFFIX or ""
            elif method == "POST":
                prefix_field = settings.app_settings.RESTFUL_POST_ROUTER_ADD_PREFIX or ""
                suffix_field = settings.app_settings.RESTFUL_POST_ROUTER_ADD_SUFFIX or ""
            elif method == "PUT":
                prefix_field = settings.app_settings.RESTFUL_PUT_ROUTER_ADD_PREFIX or ""
                suffix_field = settings.app_settings.RESTFUL_PUT_ROUTER_ADD_SUFFIX or ""
            elif method == "DELETE":
                prefix_field = settings.app_settings.RESTFUL_DELETE_ROUTER_ADD_PREFIX or ""
                suffix_field = settings.app_settings.RESTFUL_DELETE_ROUTER_ADD_SUFFIX or ""
            else:
                prefix_field = ""
                suffix_field = ""
            if prefix_field:
                prefix_field = prefix_field.strip("/") + "/"
            if suffix_field:
                suffix_field = suffix_field.strip("/") + "/"
            prefix = prefix_field + middle_field + suffix_field

            self.router_data.append(BaseRouter(router_class, func_name, func_type, method, prefix))
