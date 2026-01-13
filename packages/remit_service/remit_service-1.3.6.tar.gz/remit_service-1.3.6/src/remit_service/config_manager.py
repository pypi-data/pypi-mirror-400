"""
配置管理器 - 提供多进程/线程安全的配置管理功能
"""
import threading
import os
from typing import Dict, Any, List
from remit_service.helper import DataCent
from remit_service.log import logger


class ConfigManager:
    """配置管理器，提供线程安全的配置操作"""

    _instance = None
    _instance_lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._config_instances: Dict[str, Any] = {}
            self._config_lock = threading.RLock()
            self._initialized = True

    def register_config(self, config_key: str, config_instance):
        """注册配置实例"""
        with self._config_lock:
            self._config_instances[config_key] = config_instance

    def reload_all_configs(self):
        """重新加载所有配置"""
        with self._config_lock:
            logger.info("开始重新加载所有配置...")
            for config_key, config_instance in self._config_instances.items():
                if hasattr(config_instance, 'reload_config'):
                    config_instance.reload_config()
                    logger.debug(f"配置 {config_key} 重新加载完成")
            logger.info("所有配置重新加载完成")

    def reload_config(self, config_key: str):
        """重新加载指定配置"""
        with self._config_lock:
            if config_key in self._config_instances:
                config_instance = self._config_instances[config_key]
                if hasattr(config_instance, 'reload_config'):
                    config_instance.reload_config()
                    logger.debug(f"配置 {config_key} 重新加载完成")
                    return True
            return False

    def get_config_keys(self) -> List[str]:
        """获取所有已注册的配置键"""
        with self._config_lock:
            return list(self._config_instances.keys())

    def is_config_loaded(self, config_key: str) -> bool:
        """检查配置是否已加载"""
        with self._config_lock:
            return config_key in self._config_instances


# 全局配置管理器实例
config_manager = ConfigManager()


def watch_config_changes(config_paths: List[str], callback=None):
    """
    监控配置文件变化（可选功能）
    在生产环境中可以用来实现配置热重载
    """
    import time
    from pathlib import Path

    def default_callback():
        config_manager.reload_all_configs()

    callback = callback or default_callback

    file_mtimes = {}
    for path in config_paths:
        if os.path.exists(path):
            file_mtimes[path] = os.path.getmtime(path)

    def monitor():
        while True:
            try:
                for path in config_paths:
                    if os.path.exists(path):
                        current_mtime = os.path.getmtime(path)
                        if path not in file_mtimes or file_mtimes[path] != current_mtime:
                            file_mtimes[path] = current_mtime
                            logger.info(f"检测到配置文件变化: {path}")
                            callback()
                time.sleep(1)  # 每秒检查一次
            except Exception as e:
                logger.error(f"配置文件监控出错: {e}")
                time.sleep(5)

    # 在后台线程中运行监控
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    monitor_thread.start()
    return monitor_thread
