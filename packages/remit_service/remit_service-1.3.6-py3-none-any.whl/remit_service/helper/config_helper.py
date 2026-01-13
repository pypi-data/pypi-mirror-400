import json
import os.path
from remit_service.helper import DataCent
import threading
import yaml


def env_var_constructor(loader, node):
    value = loader.construct_scalar(node)
    var_name = value.strip('${} ')
    vars = var_name.split(",")
    if len(vars) >= 3:
        raise Exception("Invalid variable name")

    if len(vars) == 1:
        return os.getenv(var_name, "")
    else:
        return os.environ.get(vars[0], vars[-1].strip('${} '))


def config_var_constructor(loader, node):
    value = loader.construct_scalar(node)
    var_name = value.strip('${} ')
    result_dict = {}
    for pair in var_name.split(','):
        key, value = pair.split(':')
        if value in ['True', 'False']:
            result_dict[key] = value == 'True'
        elif value.isdigit():
            result_dict[key] = int(value)
        else:
            result_dict[key] = value
    return result_dict


yaml.FullLoader.add_constructor('!env', env_var_constructor)  # 为SafeLoader添加新的tag和构造器
yaml.FullLoader.add_constructor('!config', config_var_constructor)  # 为SafeLoader添加新的tag和构造器


def merge_dicts(*dicts):
    result = {}
    for d in dicts:
        for key, value in d.items():
            if isinstance(value, dict) and key in result:
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value
    return result


class ConfigLoad:
    _instance_lock = threading.Lock()

    @classmethod
    def instance(cls, config_path, service_path):
        with ConfigLoad._instance_lock:
            if not hasattr(ConfigLoad, "_instance"):
                ConfigLoad._instance = ConfigLoad(config_path, service_path)
                ConfigLoad._instance._loaded = False  # 添加加载状态标记
            else:
                # 检查路径是否变化，如果变化则更新实例
                if (ConfigLoad._instance.config_path != config_path or
                        ConfigLoad._instance.service_path != service_path):
                    # 保存当前的加载状态
                    was_loaded = getattr(ConfigLoad._instance, '_loaded', False)
                    ConfigLoad._instance = ConfigLoad(config_path, service_path)
                    # 如果之前已经加载过，保持加载状态
                    ConfigLoad._instance._loaded = was_loaded
                    from remit_service.log import logger
                    logger.debug(f"ConfigLoad实例路径变化，保持加载状态: {was_loaded}")
        return ConfigLoad._instance

    def __init__(self, config_path, service_path):
        self.config_path = config_path
        self.service_path = service_path
        self.config_file = os.path.join(self.config_path, "resources//config.yaml")
        self._loaded = False

    def load(self, force_reload=False):
        """
        智能配置加载
        :param force_reload: 是否强制重新加载
        """
        # 如果已经加载过且不强制重新加载，则跳过
        if self._loaded and not force_reload:
            from remit_service.log import logger
            logger.info("配置已加载，跳过重复加载")
            return True

        # 执行配置加载
        with open(self.config_file, encoding="utf8") as file:
            config_data = yaml.load(file.read(), Loader=yaml.FullLoader) or {}
            DataCent.update_data(config_data)

        active = DataCent.data.get("config", {}).get("active")
        if not active:
            return True

        include_config_file = os.path.join(self.config_path, f"resources//config.{active}.yaml")

        if not os.path.exists(include_config_file):
            raise FileNotFoundError(f"{include_config_file} 不存在")

        with open(include_config_file, encoding="utf8") as file:
            env_config_data = yaml.load(file.read(), Loader=yaml.FullLoader) or {}
            merged_data = merge_dicts(DataCent.data, env_config_data)
            DataCent.data = merged_data

        include = DataCent.data.get("config", {}).get("include")

        if include.get("service"):
            include_service_config_file = os.path.join(self.service_path, f"resources//config.{active}.yaml")

            if not os.path.exists(include_service_config_file):
                return True

            with open(include_service_config_file, encoding="utf8") as file:
                service_config_data = yaml.load(file.read(), Loader=yaml.FullLoader) or {}
                merged_data = merge_dicts(DataCent.data, service_config_data)
                DataCent.data = merged_data

        # 标记为已加载
        self._loaded = True

        # 通知配置管理器重新加载所有ImportConfig实例
        try:
            from remit_service.config_manager import config_manager
            config_manager.reload_all_configs()
        except ImportError:
            pass  # 如果配置管理器不可用，继续正常工作

        return True


if __name__ == '__main__':
    ConfigLoad.instance("/src/template/resources/config.yaml").load()