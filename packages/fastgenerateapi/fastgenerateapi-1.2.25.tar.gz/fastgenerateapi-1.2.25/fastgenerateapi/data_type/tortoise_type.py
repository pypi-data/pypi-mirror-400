from typing import TypeVar

from tortoise import Model

T_Model = TypeVar("T_Model", bound=Model)


