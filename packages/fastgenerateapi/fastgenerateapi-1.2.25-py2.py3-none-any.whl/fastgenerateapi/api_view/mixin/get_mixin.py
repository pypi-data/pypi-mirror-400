from fastgenerateapi.data_type.tortoise_type import T_Model


class GetMixin:

    async def set_get_model(self, model: T_Model, *args, **kwargs) -> T_Model:
        """
        修改查询后的model数据
        """
        return model

