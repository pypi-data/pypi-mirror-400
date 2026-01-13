"""
微服务调用客户端
Spring Cloud Feign 风格的装饰器实现
"""

import httpx
import asyncio
from typing import Optional, Dict, Any, Callable
from functools import wraps
from remit_service.log import logger
from .discovery import NacosServiceDiscovery


class FeignClient:
    """
    Feign 客户端装饰器
    用于声明式的微服务调用

    使用示例:
        @FeignClient("user-service")
        class UserService:
            @GetMapping("/api/user/{user_id}")
            async def get_user(self, user_id: int):
                pass

            @PostMapping("/api/user")
            async def create_user(self, user_data: dict):
                pass
    """

    # 全局服务发现实例
    _discovery: Optional[NacosServiceDiscovery] = None

    @classmethod
    def init_discovery(cls,
                      server_addr: str,
                      namespace: str = "",
                      group: str = "DEFAULT_GROUP",
                      username: Optional[str] = None,
                      password: Optional[str] = None,
                      load_balance_strategy: str = "round_robin"):
        """
        初始化全局服务发现

        Args:
            server_addr: Nacos 服务器地址
            namespace: 命名空间
            group: 分组
            username: 用户名（可选）
            password: 密码（可选）
            load_balance_strategy: 负载均衡策略
        """
        cls._discovery = NacosServiceDiscovery(
            server_addr=server_addr,
            namespace=namespace,
            group=group,
            username=username,
            password=password,
            load_balance_strategy=load_balance_strategy
        )
        logger.info("FeignClient 服务发现初始化成功")

    def __init__(self, service_name: str, timeout: int = 30, retry: int = 3):
        """
        初始化 Feign 客户端

        Args:
            service_name: 目标服务名称
            timeout: 请求超时时间（秒）
            retry: 失败重试次数
        """
        self.service_name = service_name
        self.timeout = timeout
        self.retry = retry

    def __call__(self, cls):
        """装饰器实现"""
        original_init = cls.__init__

        def new_init(instance, *args, **kwargs):
            # 调用原始的 __init__
            if original_init:
                original_init(instance, *args, **kwargs)

            # 注入服务名称和客户端配置
            instance._service_name = self.service_name
            instance._timeout = self.timeout
            instance._retry = self.retry
            instance._discovery = FeignClient._discovery

        cls.__init__ = new_init
        return cls


class RequestMapping:
    """HTTP 请求映射基类"""

    def __init__(self, path: str, method: str):
        """
        初始化请求映射

        Args:
            path: 请求路径，支持路径参数 {param}
            method: HTTP 方法 (GET, POST, PUT, DELETE, etc.)
        """
        self.path = path
        self.method = method.upper()

    def __call__(self, func: Callable):
        """装饰器实现"""
        @wraps(func)
        async def wrapper(instance, *args, **kwargs):
            # 获取服务实例
            if not hasattr(instance, '_discovery') or not instance._discovery:
                raise RuntimeError("FeignClient 未初始化，请先调用 FeignClient.init_discovery()")

            service_instance = instance._discovery.select_instance(instance._service_name)
            if not service_instance:
                raise RuntimeError(f"服务 {instance._service_name} 没有可用实例")

            # 构建完整 URL
            url_path = self.path

            # 处理路径参数 {param}
            import re
            path_params = re.findall(r'\{(\w+)\}', url_path)
            for i, param_name in enumerate(path_params):
                if param_name in kwargs:
                    url_path = url_path.replace(f'{{{param_name}}}', str(kwargs.pop(param_name)))
                elif i < len(args):
                    url_path = url_path.replace(f'{{{param_name}}}', str(args[i]))

            full_url = f"{service_instance.url}{url_path}"

            # 发送 HTTP 请求（带重试）
            retry_count = instance._retry
            last_exception = None

            for attempt in range(retry_count):
                try:
                    async with httpx.AsyncClient(timeout=instance._timeout) as client:
                        # 准备请求参数
                        request_kwargs = {}

                        # 处理请求体（POST, PUT, PATCH）
                        if self.method in ['POST', 'PUT', 'PATCH']:
                            if args:
                                request_kwargs['json'] = args[0]
                            elif kwargs:
                                request_kwargs['json'] = kwargs

                        # 处理查询参数（GET, DELETE）
                        elif self.method in ['GET', 'DELETE']:
                            if kwargs:
                                request_kwargs['params'] = kwargs

                        logger.info(f"调用服务: {self.method} {full_url}")

                        response = await client.request(
                            method=self.method,
                            url=full_url,
                            **request_kwargs
                        )

                        response.raise_for_status()

                        # 尝试解析 JSON
                        try:
                            return response.json()
                        except:
                            return response.text

                except Exception as e:
                    last_exception = e
                    if attempt < retry_count - 1:
                        logger.warning(f"请求失败，重试 {attempt + 1}/{retry_count}: {e}")
                        await asyncio.sleep(0.5 * (attempt + 1))  # 指数退避
                    else:
                        logger.error(f"请求最终失败: {self.method} {full_url}, 错误: {e}")

            raise last_exception

        return wrapper


# 便捷的 HTTP 方法装饰器
class GetMapping(RequestMapping):
    """GET 请求映射"""
    def __init__(self, path: str):
        super().__init__(path, "GET")


class PostMapping(RequestMapping):
    """POST 请求映射"""
    def __init__(self, path: str):
        super().__init__(path, "POST")


class PutMapping(RequestMapping):
    """PUT 请求映射"""
    def __init__(self, path: str):
        super().__init__(path, "PUT")


class DeleteMapping(RequestMapping):
    """DELETE 请求映射"""
    def __init__(self, path: str):
        super().__init__(path, "DELETE")


class PatchMapping(RequestMapping):
    """PATCH 请求映射"""
    def __init__(self, path: str):
        super().__init__(path, "PATCH")
