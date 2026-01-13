import asyncio

from remit_service.log import logger
import os
import threading
from fastapi.staticfiles import StaticFiles
from remit_service.base.base_app import RemitFastApi
from remit_service.base.base_router import BaseRemitAPIRouter
from remit_service.helper.config_helper import ConfigLoad
from .config import Config, ServiceConfig, NaNosConfig, RouterConfig


class FastSkeletonApp:
    _instance_lock = threading.Lock()
    app = None
    init_routes = None

    @classmethod
    def instance(cls, init_routes, title="Et Admin API接口文档管理系统"):
        with FastSkeletonApp._instance_lock:
            if not hasattr(FastSkeletonApp, "_instance"):
                FastSkeletonApp._instance = FastSkeletonApp(init_routes, title)

        return FastSkeletonApp._instance

    def _is_config_already_loaded(self):
        """检查配置是否已经加载"""
        try:
            from remit_service.helper import DataCent

            # 检查 DataCent 是否有数据
            if not DataCent.data:
                return False

            # 检查关键配置是否存在
            required_keys = ['config', 'service']
            for key in required_keys:
                if key not in DataCent.data:
                    return False

            # 检查配置是否有效（不是空字典）
            for key in required_keys:
                if not DataCent.data[key]:
                    return False

            return True

        except Exception:
            return False

    def __init__(
            self,
            init_routes,
            __file__,
            resources_path=None,
            static_dir=f"{os.path.dirname(__file__)}/static",
            middleware_func=None
    ):
        if not __file__:
            raise Exception("__file__ is required")
        if not resources_path:
            raise Exception("No resources path provided")
        self.service_path = os.path.dirname(__file__)

        # 智能配置加载：只在必要时加载，避免覆盖已有配置
        config_loader = ConfigLoad.instance(resources_path, self.service_path)
        if not self._is_config_already_loaded():
            config_loader.load()
        else:
            # 配置已加载，只验证路径是否一致
            if (config_loader.config_path != resources_path or
                    config_loader.service_path != self.service_path):
                # 路径不一致，需要重新加载
                config_loader.load()
            else:
                # 配置已正确加载，跳过重复加载
                from remit_service.log import logger
                logger.info("配置已加载，跳过重复加载以保护现有配置")
        self.app = RemitFastApi(
            prefix=RouterConfig.prefix,
            openapi_url=f"{RouterConfig.prefix}/openapi.json",
            docs_url=None,
            redoc_url=None,
            api_router_class=BaseRemitAPIRouter,
            title="Api接口",
            version='1.0'
        )

        # Nacos 服务注册（Spring Boot 风格自动配置）
        self.nacos_registry = None
        if NaNosConfig.discovery and NaNosConfig.discovery.enabled and NaNosConfig.discovery.server_addr:
            from remit_service.nacos import NacosRegistry, FeignClient

            # 初始化服务注册
            self.nacos_registry = NacosRegistry(
                service_name=ServiceConfig.service_name,
                ip=ServiceConfig.get_ip(),
                port=ServiceConfig.port,
                server_addr=NaNosConfig.discovery.server_addr,
                namespace=NaNosConfig.discovery.namespace,
                group=NaNosConfig.discovery.group,
                cluster_name=NaNosConfig.discovery.cluster_name,
                username=NaNosConfig.discovery.username,
                password=NaNosConfig.discovery.password,
                heartbeat_interval=NaNosConfig.discovery.heartbeat_interval
            )

            # 初始化 FeignClient 服务发现（用于微服务调用）
            FeignClient.init_discovery(
                server_addr=NaNosConfig.discovery.server_addr,
                namespace=NaNosConfig.discovery.namespace,
                group=NaNosConfig.discovery.group,
                username=NaNosConfig.discovery.username,
                password=NaNosConfig.discovery.password,
                load_balance_strategy="round_robin"  # 默认轮询负载均衡
            )

        self.config = Config
        self.app.HOST = ServiceConfig.ip
        self.app.PORT = ServiceConfig.port
        self.app.ServerName = ServiceConfig.service_name
        self.app.AppBaseDir = self.service_path
        self.static_dir = static_dir
        self.middleware_func = middleware_func

        # 路由配置
        self.init_routes = init_routes
        self.init()

    def init(self):

        self.app.mount(
            '/static',
            StaticFiles(directory=self.static_dir),
            name='static'
        )

        # 添加健康检查端点（Nacos 需要）
        @self.app.get("/actuator/health", include_in_schema=False)
        @self.app.get("/health", include_in_schema=False)
        async def health_check():
            """健康检查端点，供 Nacos 探测使用"""
            return {
                "status": "UP",
                "service": ServiceConfig.service_name,
                "ip": ServiceConfig.get_ip(),
                "port": ServiceConfig.port
            }

        # Nacos 自动注册和生命周期管理（Spring Boot 风格）
        if self.nacos_registry:
            @self.app.on_event("startup")
            async def nacos_startup():
                """应用启动时自动注册到 Nacos"""
                try:
                    self.nacos_registry.register()
                    self.nacos_registry.start_heartbeat()
                except Exception as e:
                    logger.error(f"Nacos 服务注册失败: {e}")

            @self.app.on_event("shutdown")
            async def nacos_shutdown():
                """应用关闭时自动从 Nacos 注销"""
                try:
                    await self.nacos_registry.stop_heartbeat()
                    self.nacos_registry.deregister()
                except Exception as e:
                    logger.error(f"Nacos 服务注销失败: {e}")

        # 批量导入注册路由
        self.init_routes(self.app)

        # 注册中间件
        if self.middleware_func:
            self.middleware_func(self.app)

        @self.app.on_event("startup")
        async def startup_event():
            logger.info(f"[Api] 【{self.app.ServerName}】-【{self.config.active}】服务启动")

        @self.app.on_event("shutdown")
        async def shutdown_event():
            logger.info(f"[Api] 【{self.app.ServerName}】-【{self.config.active}】服务关闭")


