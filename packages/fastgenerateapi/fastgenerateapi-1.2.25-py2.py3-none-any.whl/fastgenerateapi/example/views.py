from fastapi import Depends
from fastapi_cache.decorator import cache
from starlette.websockets import WebSocket

from fastgenerateapi import APIView, DeleteTreeView, GetTreeView, WebsocketView, Consumer
# from middlewares.jwt_middleware.schemas import UserObject
from fastgenerateapi.example.models import StaffInfo, CompanyInfo
from fastgenerateapi.example.schemas import CompanyInfoRead, CompanyInfoCreate, StaffReadSchema, \
    TestSchema
from fastgenerateapi.pydantic_utils.base_model import PagePydantic
from fastgenerateapi.schemas_factory.get_all_schema_factory import get_list_schema_factory


class CompanyView(APIView, DeleteTreeView, GetTreeView):
    model_class = CompanyInfo
    # response_schema = CompanyInfoRead
    # create_schema = CompanyInfoCreate

    @cache()
    async def view_get_list(self, paginator: PagePydantic = Depends()):

        return await self.get_page_data(queryset=self.queryset, fields=["id", "name"], paginator=paginator)


class StaffView(APIView):

    def __init__(self):
        self.model_class = StaffInfo
        self.order_by_fields = ["-created_at"]
        self.prefetch_related_fields = {"company": ["name"]}
        self.get_all_schema = StaffReadSchema
        # self.dependencies = [Depends(ADG.authenticate_user_deps), ]
        super().__init__()

    # async def view_get_staff_list(self, name: Optional[str] = None) -> XxxSchema:
    #     conn = Tortoise.get_connection("default")
    #     # conn = Tortoise.get_connection("local")
    #     val = await conn.execute_query_dict("SELECT * FROM information_schema.columns WHERE TABLE_NAME = 'staffinfo'")
    #     # val = await conn.execute_query_dict("SELECT * FROM staffinfo")
    #     print(val)
    #     return self.success(data=XxxSchema(**val))

    @cache()
    async def view_get_staff_list(
            self,
            paginator=Depends(PagePydantic),
            # current_user: UserObject = Depends(ADG.authenticate_user_deps),
    ) -> get_list_schema_factory(TestSchema):
        data = await self.get_page_data(queryset=self.queryset, schema=TestSchema, paginator=paginator)
        return self.success(data=data)


class ChatView(WebsocketView):
    """
    客户端与服务端场链接测试
    """
    tags = ["ws测试"]

    async def ws_wschat_pk(self, websocket: WebSocket, pk: str):
        """
        测试
        """
        await websocket.accept()
        while True:
            try:
                data = await websocket.receive_json()
                await websocket.send_text(f"接受到的消息是: {data}")
            except Exception:
                print(1)


class ChatGroupView(Consumer):
    """
    群聊测试
    """
    group_id = "group_id"
    user_id = "user_id"
    ...






