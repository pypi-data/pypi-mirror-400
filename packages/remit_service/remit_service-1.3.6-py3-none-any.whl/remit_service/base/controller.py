from __future__ import annotations

from remit_service.log import logger
import inspect
from collections.abc import Callable
from copy import deepcopy
from typing import Any, TypeVar, get_type_hints

from fastapi import APIRouter, Depends, FastAPI

from pydantic.v1.typing import is_classvar

from remit_service.base.base_router import BaseRemitAPIRouter

T = TypeVar("T")

CBV_CLASS_KEY = "__cbv_class__"


def _init_cbv(cls: type[Any]) -> None:
    """
    Idempotently modifies the provided `cls`, performing the following modifications:
    * The `__init__` function is updated to set any class-annotated dependencies as instance attributes
    * The `__signature__` attribute is updated to indicate to FastAPI what arguments should be passed to the initializer
    """
    if getattr(cls, CBV_CLASS_KEY, False):  # pragma: no cover
        return  # Already initialized
    old_init: Callable[..., Any] = cls.__init__
    old_signature = inspect.signature(old_init)
    old_parameters = list(old_signature.parameters.values())[1:]  # drop `self` parameter
    new_parameters = [
        x for x in old_parameters if x.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    ]
    dependency_names: list[str] = []
    for name, hint in get_type_hints(cls).items():
        if is_classvar(hint):
            continue
        parameter_kwargs = {"default": getattr(cls, name, Ellipsis)}
        dependency_names.append(name)
        new_parameters.append(
            inspect.Parameter(name=name, kind=inspect.Parameter.KEYWORD_ONLY, annotation=hint, **parameter_kwargs)
        )
    new_signature = old_signature.replace(parameters=new_parameters)

    def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
        for dep_name in dependency_names:
            dep_value = kwargs.pop(dep_name)
            setattr(self, dep_name, dep_value)
        old_init(self, *args, **kwargs)

    setattr(cls, "__signature__", new_signature)
    setattr(cls, "__init__", new_init)
    setattr(cls, CBV_CLASS_KEY, True)


def _update_cbv_route_endpoint_signature(cls: type[Any], endpoint: Callable[..., Any]) -> None:
    """
    Fixes the endpoint signature for a cbv route to ensure FastAPI performs dependency injection properly.
    """
    old_signature = inspect.signature(endpoint)
    old_parameters: list[inspect.Parameter] = list(old_signature.parameters.values())
    old_first_parameter = old_parameters[0]
    new_first_parameter = old_first_parameter.replace(default=Depends(cls))
    new_parameters = [new_first_parameter] + [
        parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY) for parameter in old_parameters[1:]
    ]
    new_signature = old_signature.replace(parameters=new_parameters)
    setattr(endpoint, "__signature__", new_signature)


class BaseRoute:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __call__(self, func):
        # 这里这个endpoint 对应的value 就是被装饰的函数
        # 返回的内容其实是符合self.api_add_route的入参要求
        self.kwargs["endpoint"] = func
        return self


class BaseAutoRoute:
    def __init__(self, summary=None, response_model=None, **kwargs):
        self.kwargs = kwargs
        self.kwargs["summary"] = summary
        self.kwargs["response_model"] = response_model

    def __call__(self, func):
        # 这里这个endpoint 对应的value 就是被装饰的函数
        # 返回的内容其实是符合self.api_add_route的入参要求
        methods_map = {
            "get": ["GET"],
            "post": ["POST"],
            "put": ["PUT"],
            "delete": ["DELETE"],
        }

        if func.__name__ not in methods_map:
            return self

        self.kwargs["path"] = ""
        self.kwargs["endpoint"] = func
        self.kwargs["methods"] = methods_map[func.__name__]
        return self


class __Controller:
    app = None
    url_dict = {}

    def __init__(self, __name__=None):
        self.__name__ = __name__

    @classmethod
    def init_app(cls, app: FastAPI, prefix=None):
        cls.app = app
        cls.prefix = prefix or ""

    @staticmethod
    def __add_route(router, _cls):
        # 返回被装饰类的所有方法和属性名称
        for attr_name in dir(_cls):
            if attr_name.startswith("__"):
                continue
            # 通过反射拿到对应属性的值 或方法对象本身
            attr = getattr(_cls, attr_name)
            # 添加到router上
            if isinstance(attr, (BaseRoute, BaseAutoRoute)) and hasattr(attr, "kwargs"):
                _update_cbv_route_endpoint_signature(_cls, attr.kwargs["endpoint"])

                if isinstance(attr, RequestMapping):
                    router.add_api_route(**attr.kwargs)
                elif isinstance(attr, Auto):
                    router.add_api_route(**attr.kwargs)
                elif isinstance(attr, RequestSocket):
                    router.add_websocket_route(**attr.kwargs)
                else:
                    assert False, "Cls Type is RequestMapping or WebSocket"

    def extend(self):
        def __wrapper(cls):
            _init_cbv(cls)
            if not hasattr(cls, "router"):
                raise ValueError(f"{cls} router is not defined")
            router: APIRouter = deepcopy(cls.router)
            self.__add_route(router, cls)
            self.app.include_router(router)
            cls.router = router
            return cls
        return __wrapper

    def __call__(self, prefix, tags=None, **kwargs):
        def __wrapper(cls):
            _init_cbv(cls)
            # 创建router实例
            kwargs["prefix"] = prefix
            kwargs["tags"] = tags or ["其他接口"]
            if hasattr(cls, "router"):
                raise ValueError(f"{cls} router 已经定义")
            router: APIRouter = BaseRemitAPIRouter(**kwargs)
            self.__add_route(router, cls)
            self.app.include_router(router, prefix=self.prefix)
            logger.debug(f"[Router] 注册类视图路由{tags if tags else prefix}成功！！")
            cls.router = router
            return cls
        return __wrapper

    @staticmethod
    def __auto_add_route(router, _cls):

        # 返回被装饰类的所有方法和属性名称
        for attr_name in dir(_cls):
            if attr_name.startswith("__"):
                continue
            # 通过反射拿到对应属性的值 或方法对象本身
            attr = getattr(_cls, attr_name)

            # 添加到router上
            if hasattr(attr, "kwargs") or hasattr(attr, "__name__"):

                if isinstance(attr, Auto):
                    _update_cbv_route_endpoint_signature(_cls, attr.kwargs["endpoint"])
                    router.add_api_route(**attr.kwargs)
                elif hasattr(attr, "__name__"):

                    if attr.__name__ in ("get", "post", "put", "delete"):
                        attr = Auto()(attr)
                        _update_cbv_route_endpoint_signature(_cls, attr.kwargs["endpoint"])
                        router.add_api_route(**attr.kwargs)

    def auto(self, url, tags=None, **kwargs):
        def __wrapper(cls):
            _init_cbv(cls)
            # 创建router实例
            kwargs["prefix"] = url
            kwargs["tags"] = tags or ["其他接口"]
            if hasattr(cls, "router"):
                raise ValueError(f"{cls} router 已经定义")
            router: APIRouter = BaseRemitAPIRouter(**kwargs)
            self.__auto_add_route(router, cls)
            self.app.include_router(router, prefix=self.prefix)
            logger.debug(f"[Router] 注册类视图路由{tags if tags else url}成功！！")
            cls.router = router
            return cls
        return __wrapper

    def register_router(self, url, tagger_view, tags=None, **kwargs):
        _init_cbv(tagger_view)
        # 创建router实例
        kwargs["prefix"] = url
        kwargs["tags"] = tags or ["其他接口"]
        if hasattr(tagger_view, "router"):
            router = tagger_view.router
            # raise ValueError(f"{tagger_view} router 已经定义")
        else:
            router: APIRouter = BaseRemitAPIRouter(**kwargs)
        self.__auto_add_route(router, tagger_view)
        self.app.include_router(router, prefix=self.prefix)
        logger.debug(f"[Router] 注册类视图路由{tags if tags else url}成功！！")
        tagger_view.router = router


class RequestMapping(BaseRoute): ...


class Auto(BaseAutoRoute): ...


class RequestGet(RequestMapping):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs["methods"] = ["GET"]


class RequestPost(RequestMapping):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs["methods"] = ["POST"]


class RequestPut(RequestMapping):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs["methods"] = ["PUT"]


class RequestDelete(RequestMapping):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs["methods"] = ["DELETE"]


class RequestSocket(BaseRoute): ...


Controller = __Controller()

