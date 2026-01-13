from typing import List, Union

# from _ctypes import PyObj_FromPtr
from starlette.endpoints import WebSocketEndpoint

from fastgenerateapi.channel.connection_manager import ConnectionManager


class Consumer(WebSocketEndpoint):
    """
    群聊
    """
    encoding = "json"
    group_id = None
    user_id = None

    # 连接 存储
    async def on_connect(self, websocket):
        await websocket.accept()

        # 用户输入名称
        self.group_id = websocket.path_params.get("group_id")
        self.user_id = await self.get_user_id(websocket)
        await self.group_add(websocket, self.group_id, self.user_id)
        # await self.group_send(self.group_id, {"msg": f"{self.user_id}-加入了聊天室"})

    @staticmethod
    async def get_user_id(websocket):
        return websocket.query_params.get("user_id")

    # 收消息后自动转发
    async def on_receive(self, websocket, data):
        if self.group_id:
            await self.group_send(self.group_id, data, user_id=self.user_id)

    # 断开 删除
    async def on_disconnect(self, websocket, close_code):
        if self.group_id and self.user_id:
            ConnectionManager.del_group_connection(self.group_id, self.user_id)
        pass

    async def check_args(self, group_id, user_id):
        """
        用于检查数据是否有效
        :param group_id:
        :param user_id:
        :return:
        """
        return True

    # 添加组
    async def group_add(self, websocket, group_id, user_key):
        if not group_id:
            await self.error(websocket, code=422, msg="未获取到组信息")
        if not user_key:
            await self.error(websocket, code=422, msg="未获取到用户信息")
        if not await self.check_args(group_id, user_key):
            await self.error(websocket, code=422, msg="无连接权限")
        ConnectionManager.add_group_connection(group_id, user_key, websocket)

    # 群发消息
    @classmethod
    async def group_send(cls, group_id, data, code=200, user_id=None, exclude: Union[bool, list] = True):
        """
        群发送消息
        :param group_id: 组对应的id
        :param data: 发送的数据
        :param code: 状态码
        :param user_id: 发出消息人的id，添加时默认群消息不包含自己
        :param exclude: 默认True排除自己；[int] 时可选排除其他人
        :return:
        """
        result = ConnectionManager.active_group_connections.get(group_id, {})
        if type(exclude) == bool:
            exclude = [user_id] if user_id and exclude else []
        for user_id, websocket in result.items():
            if user_id in exclude:
                continue
            await websocket.send_json({
                "code": code,
                "from": user_id,
                # "message": "请求成功",
                "data": data
            })

    @staticmethod
    async def error(websocket, code=500, msg="请求失败"):
        await websocket.send_json({
            "code": code,
            "message": msg,
        })
        await websocket.close()




