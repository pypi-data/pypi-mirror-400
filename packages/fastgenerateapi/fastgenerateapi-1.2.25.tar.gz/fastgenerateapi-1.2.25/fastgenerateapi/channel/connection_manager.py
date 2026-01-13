from typing import Dict

from starlette.websockets import WebSocket


class ConnectionManager:
    active_connections: Dict[str, WebSocket] = {}
    active_group_connections: Dict[str, Dict[str, WebSocket]] = {}

    @classmethod
    def add_connection(cls, user_id: str, websocket: WebSocket):
        conn = cls.active_connections.get(user_id)
        if conn:
            conn.close()
        cls.active_connections[user_id] = websocket

    @classmethod
    def del_connection(cls, user_id: str):
        if user_id in cls.active_connections:
            cls.active_connections[user_id].close()
            del cls.active_connections[user_id]

    @classmethod
    def add_group_connection(cls, group_id: str, user_id: str, connection: WebSocket):
        conn = cls.active_group_connections.get(group_id, {}).get(user_id)
        if conn:
            conn.close()
        cls.active_group_connections.setdefault(group_id, {})[user_id] = connection

    @classmethod
    def del_group_connection(cls, group_id: str, user_id: str):
        if group_id in cls.active_group_connections:
            user_dict = cls.active_group_connections[group_id]
            if user_id in user_dict:
                user_dict[user_id].close()
                del user_dict[user_id]
                if not user_dict:
                    del cls.active_group_connections[group_id]
