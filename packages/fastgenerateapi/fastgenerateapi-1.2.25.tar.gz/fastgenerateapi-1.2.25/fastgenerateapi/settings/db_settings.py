from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    """
        Database Settings
    """

    DB_TYPE: Optional[str] = Field(default='mysql', description="数据库类型")
    DB_HOST: Optional[str] = Field(default='127.0.0.1', description="数据库域名")
    DB_PORT: Optional[int] = Field(default='3306', description="数据库端口")
    DB_DATABASE: Optional[str] = Field(default='admin', description="数据库名")
    DB_USERNAME: Optional[str] = Field(default='root', description="数据库用户名")
    DB_PASSWORD: Optional[str] = Field(default='', description="数据库密码")

    @property
    def dsn(self):
        return f"{self.DB_TYPE.lower()}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'
    )

    # class Config:
    #     env_prefix = ''
    #     env_file = "./.env"
    #     case_sensitive = True
    #     extra = 'allow'


class PostgresqlSettings(DBSettings):
    """
        Postgresql Settings
    """
    TYPE: Optional[str] = Field(default='postgres', description="数据库类型")


class MySQLSettings(DBSettings):
    """
        MySQL Settings
    """
    ...


class LocalSettings(DBSettings):
    """
        Local Settings
    """
    TYPE: str = Field(..., description="数据库类型")





