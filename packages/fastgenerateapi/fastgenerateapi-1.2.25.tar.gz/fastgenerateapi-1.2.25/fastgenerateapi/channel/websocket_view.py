from typing import Union

from starlette.websockets import WebSocket

from fastgenerateapi.api_view.base_view import BaseView
from fastgenerateapi.channel.connection_manager import ConnectionManager
from fastgenerateapi.controller.ws_controller import WsController
from fastgenerateapi.data_type.data_type import DEPENDENCIES


class WebsocketView(BaseView):
    """
    客户端与服务器之间通信
    """
    websocket_route: Union[bool, DEPENDENCIES] = True

    def _handler_websocket_settings(self):
        self.ws_summary = WsController(self, self._get_cls_ws_func())
        for ws_router in self.ws_summary.ws_router_data:
            self._add_api_websocket_route(
                f"/{ws_router.path}",
                getattr(self, ws_router.func_name),
                dependencies=ws_router.dependencies,
            )

    @classmethod
    async def accept(cls, user_id:str, websocket: WebSocket):
        await websocket.accept()
        ConnectionManager.add_connection(user_id=user_id, websocket=websocket)

        return websocket

    @classmethod
    async def send(cls, user_id, data, code=200):
        """
        群发送消息
        :param user_id: 用户id
        :param data: 发送的数据
        :param code: 状态码
        :return:
        """
        if not user_id or not data:
            return False

        websocket = ConnectionManager.active_connections.get(user_id)
        if not websocket:
            return False
        await websocket.send_json({
            "code": code,
            "from": user_id,
            # "message": "请求成功",
            "data": data
        })

        return True

    @classmethod
    async def group_send(cls, user_id_list, data, code=200):
        """
        群发送消息
        :param user_id_list: 用户id列表
        :param data: 发送的数据
        :param code: 状态码
        :return:
        """
        if not user_id_list or not data:
            return [], user_id_list
        success_user_id_list = []
        fail_user_id_list = []
        for user_id in user_id_list:
            websocket = ConnectionManager.active_connections.get(user_id)
            if not websocket:
                fail_user_id_list.append(user_id)
                continue
            await websocket.send_json({
                "code": code,
                "from": user_id,
                # "message": "请求成功",
                "data": data
            })
            success_user_id_list.append(user_id)

        return success_user_id_list, fail_user_id_list
