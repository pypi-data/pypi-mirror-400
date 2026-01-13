from typing import List, Optional

from pydantic import validator, Field
from tortoise.contrib.pydantic import pydantic_model_creator

from fastgenerateapi.pydantic_utils.base_model import BaseModel
from fastgenerateapi.schemas_factory import get_all_schema_factory, get_one_schema_factory
from fastgenerateapi.schemas_factory.common_schema_factory import common_schema_factory
from fastgenerateapi.example.models import CompanyInfo, StaffInfo


# 方式一：使用自带的schema_factory
# 注意点：
#      1， 解决了方式二存在的问题
#      2， 增删改查默认会携带模型上的参数
class StaffReadSchema(get_one_schema_factory(
    StaffInfo,
    name="StaffReadSchema",
)):
    test_name: Optional[str]
    category_name: Optional[str]

    @validator("test_name")
    def check_test(cls, value):
        if value == "test_name":
            return "test_name11"
        return value


# 方式二：使用 pydantic 写法 继承model
#  存在问题：
#       1， 外键默认需要自己添加
#       2， 关联表字段需要自己添加
#       3， 必填字符串字段参数为空字符时，schema和model校验都不会报错

class CompanyInfoRead(BaseModel, pydantic_model_creator(
    CompanyInfo,
    name='CompanyInfoRead',
)):
    parent_id: Optional[str] = Field(default=None, description="自关联id")


class CompanyInfoCreate(BaseModel, pydantic_model_creator(
    CompanyInfo,
    name='CompanyInfoCreate',
    exclude_readonly=True,
)):
    parent_id: Optional[str] = Field(default=None, description="自关联id")


# 方式三：完全自己写
class TestSchema(BaseModel):
    name: str


