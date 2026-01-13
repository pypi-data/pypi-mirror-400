from typing import Optional, Any, Literal, Union

from tortoise import BaseDBAsyncClient, connections, transactions, fields, ForeignKeyFieldInstance
from tortoise.exceptions import ParamsError
from tortoise.fields import ForeignKeyRelation, CASCADE, OnDelete, ForeignKeyNullableRelation
from tortoise.models import MODEL


def _get_connection(connection_name: Optional[str]) -> BaseDBAsyncClient:
    """
    修改目的：当多数据库源时，@atomic()有默认的源
    :param connection_name:
    :return:
    """
    # 来源 tortoise-orm==0.25.1
    # if connection_name:
    #     connection = connections.get(connection_name)
    # elif len(connections.db_config) == 1:
    #     connection_name = next(iter(connections.db_config.keys()))
    #     connection = connections.get(connection_name)
    # else:
    #     raise ParamsError(
    #         "You are running with multiple databases, so you should specify"
    #         f" connection_name: {list(connections.db_config)}"
    #     )
    # 修改后
    if connection_name:
        connection = connections.get(connection_name)
    elif len(connections.db_config) >= 1:
        # 默认选排序第一个
        connection_name = "default" if "default" in connections.db_config else next(iter(connections.db_config.keys()))
        connection = connections.get(connection_name)
    else:
        raise ParamsError(
            "You are running with multiple databases, so you should specify"
            f" connection_name: {list(connections.db_config)}"
        )
    return connection


def ForeignKeyField(
    model_name: str,
    related_name: Union[str, None, Literal[False]] = None,
    on_delete: OnDelete = CASCADE,
    db_constraint: bool = False,
    null: bool = False,
    **kwargs: Any,
) -> Union[ForeignKeyRelation[MODEL], ForeignKeyNullableRelation[MODEL]]:
    """
    修改内容 db_constraint: bool = False
    修改目的：取消数据库外键约束
    """

    return ForeignKeyFieldInstance(
        model_name, related_name, on_delete, db_constraint=db_constraint, null=null, **kwargs
    )


transactions._get_connection = _get_connection
fields.ForeignKeyField = ForeignKeyField




