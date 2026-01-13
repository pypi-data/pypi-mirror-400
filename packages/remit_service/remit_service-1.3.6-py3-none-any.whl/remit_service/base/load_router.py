from remit_service.base.controller import Controller
from remit_service.helper.modules_helper import find_modules, import_string
from remit_service.log import logger


def __register_blueprint_model_name(app=None, __name__=None, key_attribute="", prefix="", scan_names=None):
    modules = find_modules(__name__, include_packages=True, recursive=True)
    router_list = []
    for name in modules:

        # 只找某个模块开始的，避免无意义的其他扫描
        if scan_names is not None and name.rsplit(".", 1)[-1] not in scan_names:
            continue

        module = import_string(name)
        if hasattr(module, key_attribute):
            router = getattr(module, key_attribute)
            router_list.append(router) if router not in router_list else ...

    def fn(router_obj):
        app.include_router(router, prefix=prefix)
        logger.debug(f"[Router] 注册路由{router_obj.tags}成功！！")

    list(map(lambda router_obj: fn(router_obj), router_list))


def register_nestable_blueprint_for_log(
        app=None,
        model_name=None,
        api_name="",
        scan_name=None,
        key_attribute="",
        prefix=""
):
    """

    :param app: FastApi app对象
    :param model_name: 模块名称
    :param api_name: api路径
    :param scan_name: 扫描url的文件
    :param key_attribute: 匹配的路由
    :param prefix: 路由前缀
    :return:
    """
    if not app:
        import warnings
        warnings.warn('路由注册失败,需要传入Fastapi对象实例')
        return None

    if model_name and api_name:
        model_name = f'{model_name}.{api_name}'
    elif model_name:
        ...
    else:
        import warnings
        warnings.warn('路由注册失败,外部项目名称还没定义')
        return None
    Controller.init_app(app, prefix=prefix)
    __register_blueprint_model_name(app, model_name, key_attribute, prefix, scan_name)

