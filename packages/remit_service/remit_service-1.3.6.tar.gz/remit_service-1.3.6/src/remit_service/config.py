import os
from pydantic import BaseModel, field_validator
from remit_service.helper import DataCent
from typing import Optional
from remit_service.helper.ip_helper import get_local_ip, get_public_ip
import threading


# data = DataCent.data


class ImportConfig:

    def __init__(self, config_key):
        self.__config_key__ = config_key
        self.__config__ = None
        self.__cls__ = None
        self.__lock__ = threading.RLock()  # 添加线程锁

    def __call__(self, cls):
        self.__cls__ = cls
        # 注册到配置管理器
        try:
            from remit_service.config_manager import config_manager
            config_manager.register_config(self.__config_key__, self)
        except ImportError:
            pass  # 如果配置管理器不可用，继续正常工作
        return self

    def __getattr__(self, name):
        if name.startswith("_") or name.endswith("__"):
            return super().__getattribute__(name)
        
        # 双重检查锁定模式，确保线程安全的单例初始化
        if not self.__config__:
            with self.__lock__:
                if not self.__config__:  # 再次检查，避免重复初始化
                    # 使用 DataCent 的线程安全方法获取配置
                    config_data = DataCent.get_nested_value(self.__config_key__, {})
                    self.__config__ = self.__cls__(**config_data)

        return self.__config__.__getattribute__(name)
    
    def reload_config(self):
        """重新加载配置，用于配置更新时刷新"""
        with self.__lock__:
            self.__config__ = None


@ImportConfig("config")
class Config(BaseModel):
    active: str


@ImportConfig("service")
class ServiceConfig(BaseModel):
    ip: str = ""
    ip_type: str = "local"
    port: int = 8080
    service_name: str = "service"

    def __init__(self, **kwargs):
        if "ip" not in kwargs:
            kwargs["ip"] = "0.0.0.0"
            kwargs["ip_type"] = "public"
        elif kwargs.get("ip") == "0.0.0.0":
            kwargs["ip_type"] = "local_public"
        super().__init__(**kwargs)

    @classmethod
    def get_ip(cls):
        if ServiceConfig.ip_type == "local_public":
            return get_local_ip()
        if ServiceConfig.ip_type == "local":
            return "127.0.0.1"
        if ServiceConfig.ip_type == "public":
            return get_public_ip()


@ImportConfig("router")
class RouterConfig(BaseModel):
    prefix: str = ""


@ImportConfig("cloud.nacos")
class NaNosConfig(BaseModel):
    class __Discovery(BaseModel):
        enabled: bool = True  # 是否启用 Nacos 服务发现
        server_addr: str = ""  # Nacos 服务器地址
        namespace: str = ""  # 命名空间
        group: str = "DEFAULT_GROUP"  # 分组
        cluster_name: str = "DEFAULT"  # 集群名称
        username: Optional[str] = None  # 用户名（可选，不需要验证时不填）
        password: Optional[str] = None  # 密码（可选，不需要验证时不填）
        heartbeat_interval: int = 3  # 心跳间隔（秒）

    discovery: Optional[__Discovery] = None

# print(Config.active)

# print(Config.active)