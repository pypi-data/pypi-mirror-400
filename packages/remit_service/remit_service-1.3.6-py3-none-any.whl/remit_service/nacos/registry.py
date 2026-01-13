"""
Nacos 服务注册核心类
提供自动注册、心跳维护、优雅下线功能
"""

import asyncio
from typing import Optional
from remit_service.log import logger


class NacosRegistry:
    """
    Nacos 服务注册管理器
    Spring Boot 风格的自动配置和生命周期管理
    """

    def __init__(self,
                 service_name: str,
                 ip: str,
                 port: int,
                 server_addr: str,
                 namespace: str = "",
                 group: str = "DEFAULT_GROUP",
                 cluster_name: str = "DEFAULT",
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 heartbeat_interval: int = 5):
        """
        初始化 Nacos 注册器

        Args:
            service_name: 服务名称
            ip: 服务 IP
            port: 服务端口
            server_addr: Nacos 服务器地址
            namespace: 命名空间（可选）
            group: 分组（默认 DEFAULT_GROUP）
            cluster_name: 集群名称（默认 DEFAULT）
            username: 用户名（可选，不需要验证时不填）
            password: 密码（可选，不需要验证时不填）
            heartbeat_interval: 心跳间隔（秒，默认 5）
        """
        self.service_name = service_name
        self.ip = ip
        self.port = port
        self.server_addr = server_addr
        self.namespace = namespace
        self.group = group
        self.cluster_name = cluster_name
        self.username = username
        self.password = password
        self.heartbeat_interval = heartbeat_interval

        self.client = None
        self._heartbeat_task = None
        self._is_registered = False

    def _init_client(self):
        """初始化 Nacos 客户端"""
        if self.client:
            return

        try:
            from nacos import NacosClient

            # 构建客户端参数
            client_params = {
                'server_addresses': self.server_addr,
                'namespace': self.namespace
            }

            # 如果提供了用户名和密码，则添加认证信息
            if self.username and self.password:
                client_params['username'] = self.username
                client_params['password'] = self.password
                logger.info(f"Nacos 客户端初始化（带认证）: {self.server_addr}")
            else:
                logger.info(f"Nacos 客户端初始化（无认证）: {self.server_addr}")

            self.client = NacosClient(**client_params)

        except ImportError:
            logger.error("未安装 nacos-sdk-python，请执行: pip install nacos-sdk-python")
            raise
        except Exception as e:
            logger.error(f"Nacos 客户端初始化失败: {e}")
            raise

    def register(self):
        """
        注册服务到 Nacos
        支持重试机制
        """
        if self._is_registered:
            logger.warning(f"服务 {self.service_name} 已经注册，跳过重复注册")
            return

        self._init_client()

        try:
            # 注册为持久实例
            # Python Nacos SDK 的临时实例心跳不稳定，使用持久实例更可靠
            # Nacos 会通过 TCP 端口检查服务是否存活
            self.client.add_naming_instance(
                service_name=self.service_name,
                ip=self.ip,
                port=self.port,
                cluster_name=self.cluster_name if self.cluster_name else "DEFAULT",
                group_name=self.group if self.group else "DEFAULT_GROUP",
                ephemeral=False,  # 持久实例
                healthy=True  # 初始状态为健康
            )
            self._is_registered = True
            logger.info(
                f"✓ Nacos 服务注册成功 - "
                f"服务: {self.service_name}, "
                f"地址: {self.ip}:{self.port}, "
                f"分组: {self.group}, "
                f"集群: {self.cluster_name}, "
                f"类型: 持久实例（TCP 健康检查）"
            )
        except Exception as e:
            logger.error(f"✗ Nacos 服务注册失败: {e}")
            logger.error(f"注册参数 - 服务: {self.service_name}, IP: {self.ip}, 端口: {self.port}, 分组: {self.group}, 集群: {self.cluster_name}")
            raise

    def deregister(self):
        """
        从 Nacos 注销服务
        优雅下线
        """
        if not self._is_registered or not self.client:
            return

        try:
            self.client.remove_naming_instance(
                service_name=self.service_name,
                ip=self.ip,
                port=self.port,
                cluster_name=self.cluster_name,
                group_name=self.group
            )
            self._is_registered = False
            logger.info(f"✓ Nacos 服务注销成功 - 服务: {self.service_name}")
        except Exception as e:
            logger.error(f"✗ Nacos 服务注销失败: {e}")

    async def _heartbeat_loop(self):
        """
        状态监控循环
        持久实例由 Nacos 服务端通过 TCP 检查健康状态
        这里只监控实例是否还在注册列表中
        """
        logger.info(f"Nacos 状态监控启动 - 间隔: {self.heartbeat_interval * 6}秒")

        while self._is_registered:
            try:
                # 每 30 秒检查一次状态
                await asyncio.sleep(self.heartbeat_interval * 6)

                if not self._is_registered:
                    break

                # 检查实例是否还在注册列表中
                try:
                    instances = self.client.list_naming_instance(
                        service_name=self.service_name,
                        group_name=self.group
                    )
                    found = False
                    if instances and 'hosts' in instances:
                        for host in instances['hosts']:
                            if host['ip'] == self.ip and host['port'] == self.port:
                                found = True
                                healthy = host.get('healthy', False)
                                status = "健康" if healthy else "不健康（Nacos 通过 TCP 检查中）"
                                logger.info(f"✓ 服务实例状态: {status} - {self.service_name} ({self.ip}:{self.port})")
                                break

                    if not found:
                        logger.error(f"✗ 服务实例未找到，尝试重新注册 - {self.service_name}")
                        self._is_registered = False
                        self.register()

                except Exception as check_error:
                    logger.error(f"服务状态检查失败: {check_error}")

            except asyncio.CancelledError:
                logger.info("Nacos 状态监控被取消")
                break
            except Exception as e:
                logger.error(f"Nacos 状态监控异常: {e}")
                await asyncio.sleep(self.heartbeat_interval * 6)

    def start_heartbeat(self):
        """
        启动心跳任务
        返回 asyncio.Task 供 FastAPI 管理
        """
        if self._heartbeat_task and not self._heartbeat_task.done():
            logger.warning("心跳任务已在运行")
            return self._heartbeat_task

        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        return self._heartbeat_task

    async def stop_heartbeat(self):
        """
        停止心跳任务
        """
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            logger.info("Nacos 心跳任务已停止")
