"""
Nacos 服务注册与发现模块
Spring Boot 风格的自动配置和注册
"""

from .registry import NacosRegistry
from .discovery import NacosServiceDiscovery, ServiceInstance, LoadBalancer
from .client import (
    FeignClient,
    GetMapping,
    PostMapping,
    PutMapping,
    DeleteMapping,
    PatchMapping
)

__all__ = [
    'NacosRegistry',
    'NacosServiceDiscovery',
    'ServiceInstance',
    'LoadBalancer',
    'FeignClient',
    'GetMapping',
    'PostMapping',
    'PutMapping',
    'DeleteMapping',
    'PatchMapping'
]
