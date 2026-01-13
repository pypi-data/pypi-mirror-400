from typing import Optional, Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EtcdSettings(BaseSettings):
    """
        Etcd Settings
    """
    ETCD_SETTING_KEY: Optional[str] = Field(default=None, description="当使用etcd做配置储存时的键值")
    ETCD_HOST: Optional[str] = Field(default='localhost', description="地址")
    ETCD_PORT: Optional[int] = Field(default=2379, description="端口")
    ETCD_CA_CERT: Optional[str] = Field(default=None, description="Ca证书")
    ETCD_CERT_KEY: Optional[str] = Field(default=None, description="证书key")
    ETCD_CERT_CERT: Optional[str] = Field(default=None, description="证书密钥")
    ETCD_TIMEOUT: Optional[int] = Field(default=None, description="超时试剂")
    ETCD_USER: Optional[str] = Field(default=None, description="账号")
    ETCD_PASSWORD: Optional[str] = Field(default=None, description="密码")
    ETCD_GRPC_OPTIONS: Optional[Any] = Field(default=None, description="grpc参数")

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        case_sensitive=True,
        extra='ignore',
        frozen=True,
    )

    @property
    def client(self):
        import etcd3
        etcd_dict = self.model_dump(exclude_unset=True, by_alias=True, exclude={"ETCD_SETTING_KEY", })
        etcd = etcd3.client(**{key.removeprefix("ETCD_").lower(): value for key, value in etcd_dict.items()})

        return etcd



