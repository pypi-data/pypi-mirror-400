"""
Nacos 服务发现模块
从 Nacos 获取服务实例列表
"""

import random
from typing import List, Optional, Dict
from remit_service.log import logger


class ServiceInstance:
    """服务实例信息"""

    def __init__(self, ip: str, port: int, weight: float = 1.0, healthy: bool = True, metadata: Dict = None):
        self.ip = ip
        self.port = port
        self.weight = weight
        self.healthy = healthy
        self.metadata = metadata or {}

    @property
    def url(self) -> str:
        """获取服务实例的 URL"""
        return f"http://{self.ip}:{self.port}"

    def __repr__(self):
        return f"ServiceInstance(ip={self.ip}, port={self.port}, healthy={self.healthy})"


class LoadBalancer:
    """负载均衡器"""

    def __init__(self, strategy: str = "round_robin"):
        """
        初始化负载均衡器

        Args:
            strategy: 负载均衡策略 (round_robin, random, weight)
        """
        self.strategy = strategy
        self._round_robin_index = 0

    def select(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """
        从实例列表中选择一个实例

        Args:
            instances: 服务实例列表

        Returns:
            选中的服务实例，如果没有可用实例则返回 None
        """
        # 过滤出健康的实例
        healthy_instances = [inst for inst in instances if inst.healthy]

        if not healthy_instances:
            logger.warning("没有可用的健康实例")
            return None

        if self.strategy == "random":
            return random.choice(healthy_instances)

        elif self.strategy == "weight":
            return self._weighted_select(healthy_instances)

        else:  # round_robin (默认)
            instance = healthy_instances[self._round_robin_index % len(healthy_instances)]
            self._round_robin_index += 1
            return instance

    def _weighted_select(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """基于权重的选择"""
        total_weight = sum(inst.weight for inst in instances)
        if total_weight == 0:
            return random.choice(instances)

        rand_weight = random.uniform(0, total_weight)
        current_weight = 0

        for instance in instances:
            current_weight += instance.weight
            if current_weight >= rand_weight:
                return instance

        return instances[-1]


class NacosServiceDiscovery:
    """
    Nacos 服务发现
    从 Nacos 获取服务实例并提供负载均衡
    """

    def __init__(self,
                 server_addr: str,
                 namespace: str = "",
                 group: str = "DEFAULT_GROUP",
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 load_balance_strategy: str = "round_robin"):
        """
        初始化服务发现

        Args:
            server_addr: Nacos 服务器地址
            namespace: 命名空间
            group: 分组
            username: 用户名（可选）
            password: 密码（可选）
            load_balance_strategy: 负载均衡策略 (round_robin, random, weight)
        """
        self.server_addr = server_addr
        self.namespace = namespace
        self.group = group
        self.username = username
        self.password = password
        self.client = None
        self.load_balancer = LoadBalancer(load_balance_strategy)

        self._init_client()

    def _init_client(self):
        """初始化 Nacos 客户端"""
        if self.client:
            return

        try:
            from nacos import NacosClient

            client_params = {
                'server_addresses': self.server_addr,
                'namespace': self.namespace
            }

            if self.username and self.password:
                client_params['username'] = self.username
                client_params['password'] = self.password

            self.client = NacosClient(**client_params)
            logger.info(f"Nacos 服务发现客户端初始化成功: {self.server_addr}")

        except ImportError:
            logger.error("未安装 nacos-sdk-python，请执行: pip install nacos-sdk-python")
            raise
        except Exception as e:
            logger.error(f"Nacos 服务发现客户端初始化失败: {e}")
            raise

    def get_instances(self, service_name: str) -> List[ServiceInstance]:
        """
        获取服务的所有实例

        Args:
            service_name: 服务名称

        Returns:
            服务实例列表
        """
        try:
            instances = self.client.list_naming_instance(
                service_name=service_name,
                group_name=self.group
            )

            if not instances or 'hosts' not in instances:
                logger.warning(f"服务 {service_name} 没有可用实例")
                return []

            service_instances = []
            for host in instances['hosts']:
                instance = ServiceInstance(
                    ip=host['ip'],
                    port=host['port'],
                    weight=host.get('weight', 1.0),
                    healthy=host.get('healthy', True),
                    metadata=host.get('metadata', {})
                )
                service_instances.append(instance)

            logger.info(f"服务 {service_name} 发现 {len(service_instances)} 个实例")
            return service_instances

        except Exception as e:
            logger.error(f"获取服务实例失败: {service_name}, 错误: {e}")
            return []

    def select_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """
        选择一个服务实例（带负载均衡）

        Args:
            service_name: 服务名称

        Returns:
            选中的服务实例，如果没有可用实例则返回 None
        """
        instances = self.get_instances(service_name)
        if not instances:
            return None

        instance = self.load_balancer.select(instances)
        if instance:
            logger.info(f"选择服务实例: {service_name} -> {instance.url}")

        return instance
