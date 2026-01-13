from fastapi import FastAPI, routing
from fastapi.datastructures import Default
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse

from remit_service.config import RouterConfig


class RemitFastApi(FastAPI):
    def __init__(
            self,
            *args,
            api_router_class=routing.APIRouter,
            router_class_args=None,
            default_response_class=Default(JSONResponse),
            generate_unique_id_function=Default(generate_unique_id),
            **kwargs
    ):
        self.HOST = None
        self.PORT = None
        self.ServerName = None
        self.AppBaseDir = None
        super().__init__(*args, **kwargs)
        self.router_class_args = router_class_args or {}
        self.router: routing.APIRouter = api_router_class(
            prefix=kwargs.get("prefix"),
            routes=self.routes,
            redirect_slashes=kwargs.get("redirect_slashes") or True,
            dependency_overrides_provider=self,
            on_startup=kwargs.get("on_startup"),
            on_shutdown=kwargs.get("on_shutdown"),
            lifespan=kwargs.get("lifespan"),
            default_response_class=default_response_class,
            dependencies=kwargs.get("dependencies"),
            callbacks=kwargs.get("callbacks"),
            deprecated=kwargs.get("deprecated"),
            include_in_schema=kwargs.get("include_in_schema") or True,
            responses=kwargs.get("responses"),
            generate_unique_id_function=generate_unique_id_function,

        )
