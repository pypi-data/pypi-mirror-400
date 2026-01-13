import threading
from typing import Dict, Any


class __DataCent:
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._lock = threading.RLock()  # 使用递归锁支持嵌套调用

    @property
    def data(self) -> Dict[str, Any]:
        with self._lock:
            return self._data.copy()  # 返回副本避免外部修改

    @data.setter
    def data(self, value: Dict[str, Any]):
        with self._lock:
            self._data = value.copy() if value else {}

    def update_data(self, new_data: Dict[str, Any]):
        """线程安全的数据更新方法"""
        with self._lock:
            if new_data:
                self._data.update(new_data)

    def get_nested_value(self, key_path: str, default=None):
        """线程安全的嵌套键值获取"""
        with self._lock:
            keys = key_path.split(".")
            data = self._data
            for key in keys:
                if isinstance(data, dict) and key in data:
                    data = data[key]
                else:
                    return default
            return data


DataCent = __DataCent()