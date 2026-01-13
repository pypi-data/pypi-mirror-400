# FastAPI Remit Service

🚀 **企业级 FastAPI 微服务框架** - Spring Boot 风格的 Python 微服务解决方案

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Nacos](https://img.shields.io/badge/Nacos-2.0+-orange.svg)](https://nacos.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ 核心特性

### 🎯 微服务架构
- ✅ **Nacos 服务注册与发现** - Spring Cloud 风格的自动配置
- ✅ **FeignClient 声明式调用** - 类似 Spring Cloud OpenFeign
- ✅ **负载均衡** - 支持轮询、随机、权重策略
- ✅ **健康检查** - 自动心跳和实例监控
- ✅ **优雅下线** - 服务关闭时自动注销

### 🛠️ 框架能力
- ✅ **类视图** - 面向对象的路由定义
- ✅ **蓝图路由** - 模块化路由管理
- ✅ **多配置文件** - 支持多环境配置
- ✅ **配置注入** - Pydantic 模型自动注入
- ✅ **服务管理** - 完整的生命周期管理

----

## 📦 安装

```bash
pip install fastapi uvicorn nacos-sdk-python pydantic pyyaml httpx loguru
```

----

## ⚙️ 配置管理

### 配置文件结构

框架使用 **YAML** 格式的配置文件，支持多环境配置。

```
project/
└── resources/              # 配置文件目录（必须）
    ├── config.yaml        # 主配置文件
    ├── config.dev.yaml    # 开发环境配置
    ├── config.test.yaml   # 测试环境配置
    └── config.prod.yaml   # 生产环境配置
```

> **注意**: `resources` 目录是必须存在的，框架会自动定位此目录加载配置文件。

### 1. 单体项目配置

#### 主配置文件 `resources/config.yaml`

```yaml
config:
  # 激活环境，从 ENV 环境变量获取，默认为 dev
  active: !env ${ENV, dev}
```

#### 环境配置文件 `resources/config.dev.yaml`

```yaml
service:
  ip: 0.0.0.0              # 服务监听 IP
  port: 9066               # 服务端口
  service_name: user-service  # 服务名称

# Nacos 服务发现配置（可选）
nacos:
  discovery:
    enabled: true
    server_addr: 192.168.20.10:8848
    namespace: ""
    group: test
    cluster_name: default
    heartbeat_interval: 5
```

### 2. 多服务项目配置

#### 主配置文件 `resources/config.yaml`

```yaml
config:
  active: !env ${ENV, dev}
  # 引入当前启动服务的配置文件
  include: !config ${service:True}
```

**说明**:
- `include`: 引入额外的配置文件
- `!config ${service:True}`: 自动加载当前启动服务的配置文件

#### 服务配置文件 `a_service/resources/config.dev.yaml`

```yaml
service:
  ip: 0.0.0.0
  port: 9066
  service_name: a-service

nacos:
  discovery:
    enabled: true
    server_addr: 192.168.20.10:8848
    group: test
```

### 3. 配置注入

使用 Pydantic 模型自动注入配置。

#### 配置文件 `resources/config.dev.yaml`

```yaml
service:
  ip: 0.0.0.0
  port: 9066
  service_name: user-service

# 自定义配置
database:
  host: localhost
  port: 3306
  username: root
  password: 123456
  database: mydb

redis:
  host: localhost
  port: 6379
  password: ""
  db: 0
```

#### 配置模型 `config.py`

```python
from pydantic import BaseModel
from remin_service.config import ImportConfig

@ImportConfig("database")
class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: str
    port: int
    username: str
    password: str
    database: str

@ImportConfig("redis")
class RedisConfig(BaseModel):
    """Redis 配置"""
    host: str
    port: int
    password: str = ""
    db: int = 0
```

#### 使用配置

```python
from config import DatabaseConfig, RedisConfig

# 直接使用配置
print(f"数据库地址: {DatabaseConfig.host}:{DatabaseConfig.port}")
print(f"Redis 地址: {RedisConfig.host}:{RedisConfig.port}")
```

----

## 🚀 快速开始

### 1. 项目结构

```
project/
├── resources/              # 配置文件目录
│   ├── config.yaml
│   └── config.dev.yaml
├── view/                   # 视图层（控制器）
│   ├── __init__.py
│   └── user.py
├── config.py               # 配置模型
├── init_router.py          # 路由注册
└── main.py                 # 启动文件
```

### 2. 定义视图（控制器）

```python
# view/user.py
from remin_service.base.controller import Controller, RequestGet, RequestPost

@Controller(prefix="/api/user", tags=["用户管理"])
class UserView:
    """用户管理控制器"""
    
    @RequestGet(path="/list")
    async def list_users(self):
        """GET 请求"""
        pass
    
    @RequestPost(path="/create")
    async def create_user(self):
        """POST 请求"""
        pass
    
    @RequestPut(path="/{user_id}")
    async def update_user(self, user_id: int):
        """PUT 请求"""
        pass
    
    @RequestDelete(path="/{user_id}")
    async def delete_user(self, user_id: int):
        """DELETE 请求"""
        pass
    
    @RequestPatch(path="/{user_id}")
    async def patch_user(self, user_id: int):
        """PATCH 请求"""
        pass
```

### 3. 注册路由

```python
# init_router.py
from remin_service.base.load_router import register_nestable_blueprint_for_log

def init_routes(fastapi_app):
    """注册所有路由"""
    # 自动扫描并注册 view 目录下的所有控制器
    register_nestable_blueprint_for_log(
        fastapi_app, 
        __name__, 
        api_name='user'
    )
```

### 4. 启动服务

```python
# main.py
import os
import uvicorn
from remin_service.app import FastSkeletonApp
from init_router import init_routes

# 配置文件路径
resources_path = os.path.join(os.path.dirname(__file__), "resources")

# 创建应用
app = FastSkeletonApp(
    init_routes,
    __file__,
    resources_path=resources_path
).app

if __name__ == '__main__':
    # 启动服务
    uvicorn.run(
        app=app, 
        host=app.HOST, 
        port=app.PORT,
        log_level="info"
    )
```

### 5. 运行

```bash
# 开发环境
python main.py

# 指定环境
ENV=prod python main.py

# 使用 uvicorn 启动
uvicorn main:app --host 0.0.0.0 --port 9066 --reload
```

### 6. 访问 API 文档

启动后访问：

- **Swagger UI**: http://localhost:9066/docs
- **ReDoc**: http://localhost:9066/redoc
- **OpenAPI JSON**: http://localhost:9066/openapi.json

----

## 🎨 控制器装饰器

框架提供了丰富的装饰器用于定义路由：

```python
from remin_service.base.controller import (
    Controller,
    RequestGet,
    RequestPost,
    RequestPut,
    RequestDelete,
    RequestPatch
)

@Controller(prefix="/api/user", tags=["用户管理"])
class UserView:
    
    @RequestGet(path="/list")
    async def list_users(self):
        """GET 请求"""
        pass
    
    @RequestPost(path="/create")
    async def create_user(self):
        """POST 请求"""
        pass
    
    @RequestPut(path="/{user_id}")
    async def update_user(self, user_id: int):
        """PUT 请求"""
        pass
    
    @RequestDelete(path="/{user_id}")
    async def delete_user(self, user_id: int):
        """DELETE 请求"""
        pass
    
    @RequestPatch(path="/{user_id}")
    async def patch_user(self, user_id: int):
        """PATCH 请求"""
        pass
```

----

## 🔧 Nacos 配置详解

### 配置文件

```yaml
# resources/config.dev.yaml
nacos:
  discovery:
    enabled: true                          # 是否启用 Nacos
    server_addr: 192.168.20.10:8848       # Nacos 服务器地址
    namespace: ""                          # 命名空间（默认 public）
    group: test                            # 分组（默认 DEFAULT_GROUP）
    cluster_name: default                  # 集群名称
    username: nacos                        # 用户名（可选）
    password: nacos                        # 密码（可选）
    heartbeat_interval: 5                  # 心跳间隔（秒）
```

### 服务注册

服务启动时会自动注册到 Nacos：

```
✓ Nacos 服务注册成功
  - 服务: user-service
  - 地址: 192.168.20.11:9066
  - 分组: test
  - 集群: default
  - 类型: 持久实例（TCP 健康检查）
```

### 健康检查

框架自动提供健康检查端点：

- `/actuator/health` - Spring Boot 风格
- `/health` - 简化版本

Nacos 会定期通过 TCP 检查服务端口，确保服务健康。

---

## 🌟 FeignClient 使用指南

### 1. 基本用法

```python
from remin_service.nacos import FeignClient, GetMapping, PostMapping, PutMapping, DeleteMapping

@FeignClient("user-service")
class UserServiceClient:
    """用户服务客户端"""
    
    @GetMapping("/api/user/{user_id}")
    async def get_user(self, user_id: int):
        """获取用户"""
        pass
    
    @PostMapping("/api/user")
    async def create_user(self, name: str, email: str):
        """创建用户"""
        pass
    
    @PutMapping("/api/user/{user_id}")
    async def update_user(self, user_id: int, name: str):
        """更新用户"""
        pass
    
    @DeleteMapping("/api/user/{user_id}")
    async def delete_user(self, user_id: int):
        """删除用户"""
        pass
```

### 2. 路径参数

支持 Spring Boot 风格的路径参数：

```python
@GetMapping("/api/user/{user_id}/orders/{order_id}")
async def get_order(self, user_id: int, order_id: int):
    pass

# 调用
client = UserServiceClient()
order = await client.get_order(user_id=1, order_id=100)
```

### 3. 查询参数

GET 和 DELETE 请求自动处理查询参数：

```python
@GetMapping("/api/users")
async def list_users(self, page: int = 1, size: int = 10):
    pass

# 调用
users = await client.list_users(page=1, size=20)
# 实际请求: GET /api/users?page=1&size=20
```

### 4. 请求体

POST、PUT、PATCH 请求自动处理 JSON 请求体：

```python
@PostMapping("/api/user")
async def create_user(self, user_data: dict):
    pass

# 调用
user = await client.create_user({
    "name": "张三",
    "email": "zhangsan@example.com"
})
```

### 5. 超时和重试

```python
@FeignClient("user-service", timeout=60, retry=5)
class UserServiceClient:
    """
    timeout: 请求超时时间（秒），默认 30
    retry: 失败重试次数，默认 3
    """
    pass
```

---

## 📊 负载均衡

### 支持的策略

1. **轮询（round_robin）** - 默认策略
2. **随机（random）** - 随机选择实例
3. **权重（weighted）** - 根据权重分配流量

### 配置负载均衡

```python
# app.py
FeignClient.init_discovery(
    server_addr=NaNosConfig.discovery.server_addr,
    namespace=NaNosConfig.discovery.namespace,
    group=NaNosConfig.discovery.group,
    load_balance_strategy="round_robin"  # 轮询 | random | weighted
)
```

### 多实例示例

```
服务: user-service
实例 1: 192.168.20.11:9066
实例 2: 192.168.20.12:9066
实例 3: 192.168.20.13:9066

轮询策略:
请求 1 → 实例 1
请求 2 → 实例 2
请求 3 → 实例 3
请求 4 → 实例 1
...
```

---

## 🏗️ 完整示例

### 项目结构

```
microservices/
├── user-service/              # 用户服务
│   ├── resources/
│   │   ├── config.yaml
│   │   └── config.dev.yaml
│   ├── view/
│   │   └── user.py
│   ├── config.py
│   ├── init_router.py
│   └── main.py
│
├── order-service/             # 订单服务
│   ├── resources/
│   │   ├── config.yaml
│   │   └── config.dev.yaml
│   ├── view/
│   │   └── order.py
│   ├── client/
│   │   └── user_client.py    # 用户服务客户端
│   ├── config.py
│   ├── init_router.py
│   └── main.py
│
└── product-service/           # 商品服务
    ├── resources/
    ├── view/
    └── main.py
```

### 用户服务

```python
# user-service/view/user.py
from remin_service.base.controller import Controller, RequestGet

@Controller(prefix="/api/user", tags=["用户管理"])
class UserView:
    
    @RequestGet(path="/{user_id}")
    async def get_user(self, user_id: int):
        return {
            "code": 200,
            "message": "成功",
            "data": {
                "id": user_id,
                "name": "张三",
                "email": "zhangsan@example.com"
            }
        }
```

### 订单服务

```python
# order-service/client/user_client.py
from remin_service.nacos import FeignClient, GetMapping

@FeignClient("user-service")
class UserServiceClient:
    @GetMapping("/api/user/{user_id}")
    async def get_user(self, user_id: int):
        pass

# order-service/view/order.py
from remin_service.base.controller import Controller, RequestPost
from ..client.user_client import UserServiceClient

@Controller(prefix="/api/order", tags=["订单管理"])
class OrderView:
    
    @RequestPost(path="/create")
    async def create_order(self, user_id: int, product_id: int):
        # 调用用户服务
        user_client = UserServiceClient()
        user = await user_client.get_user(user_id=user_id)
        
        # 创建订单
        order = {
            "order_id": 12345,
            "user": user["data"],
            "product_id": product_id,
            "status": "pending"
        }
        
        return {
            "code": 200,
            "message": "订单创建成功",
            "data": order
        }
```

---

## 🔍 日志示例

### 服务启动

```
2025-12-01 17:00:00 | INFO | Nacos 客户端初始化: 192.168.20.10:8848
2025-12-01 17:00:00 | INFO | ✓ Nacos 服务注册成功 - 服务: user-service, 地址: 192.168.20.11:9066
2025-12-01 17:00:00 | INFO | FeignClient 服务发现初始化成功
2025-12-01 17:00:00 | INFO | [Api] 【user-service】-【dev】服务启动
```

### 服务调用

```
2025-12-01 17:00:10 | INFO | 服务 user-service 发现 2 个实例
2025-12-01 17:00:10 | INFO | 选择服务实例: user-service -> http://192.168.20.11:9066
2025-12-01 17:00:10 | INFO | 调用服务: GET http://192.168.20.11:9066/api/user/1
```

### 健康检查

```
2025-12-01 17:00:30 | INFO | ✓ 服务实例健康 - user-service (192.168.20.11:9066)
```

---

## 🚨 常见问题

### 1. 服务注册失败（400 错误）

**原因**: Nacos 版本不兼容或参数不支持

**解决**: 框架已使用最简参数注册，兼容所有 Nacos 版本

### 2. 服务实例显示不健康

**原因**: Nacos 通过 TCP 检查服务端口，可能有延迟

**解决**: 等待 5-10 秒，Nacos 会自动更新状态

### 3. 服务调用失败

**检查清单**:
- ✅ 服务是否已注册到 Nacos
- ✅ 服务名称是否正确
- ✅ 网络是否可达
- ✅ 目标服务是否正常运行

### 4. 负载均衡不生效

**原因**: 只有一个服务实例

**解决**: 启动多个实例，负载均衡会自动生效

---

## 📚 API 文档

启动服务后访问：

- Swagger UI: `http://localhost:9066/docs`
- ReDoc: `http://localhost:9066/redoc`
- OpenAPI JSON: `http://localhost:9066/openapi.json`

---

## 🤝 对比 Spring Cloud

| 功能 | Spring Cloud | FastAPI Remit Service |
|------|--------------|----------------------|
| 服务注册 | `@EnableDiscoveryClient` | 自动注册（配置启用） |
| 服务调用 | `@FeignClient` | `@FeignClient` |
| 负载均衡 | Ribbon | 内置（轮询/随机/权重） |
| 配置管理 | Spring Cloud Config | YAML 多环境配置 |
| 健康检查 | Actuator | `/actuator/health` |
| 服务发现 | Eureka/Nacos | Nacos |

---

## 📝 License

MIT License

---

## 🙏 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Nacos](https://nacos.io/) - 动态服务发现和配置管理平台
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证和设置管理
- [Uvicorn](https://www.uvicorn.org/) - ASGI 服务器

---

## 📧 联系方式

如有问题或建议，欢迎提 Issue 或 PR！

**Happy Coding! 🎉**