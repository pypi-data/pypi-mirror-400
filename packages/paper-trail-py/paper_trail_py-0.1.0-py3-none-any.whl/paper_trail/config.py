"""
全局配置管理
~~~~~~~~~~~

集中管理 PaperTrail 的配置选项
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PaperTrailConfig:
    """全局配置"""

    # 是否启用追踪（全局开关）
    enabled: bool = True

    # 版本表名称
    version_table_name: str = "versions"

    # 默认忽略的字段
    default_ignore_fields: set = field(
        default_factory=lambda: {
            "updated_at",
            "modified_at",
            "last_modified",
        }
    )

    # 是否存储完整对象快照
    store_object_snapshot: bool = True

    # 是否存储变更增量
    store_object_changes: bool = True

    # 性能优化：批量插入阈值
    batch_insert_threshold: int = 100

    # 是否启用异步支持
    async_enabled: bool = False

    # 自定义元数据
    metadata: dict[str, Any] = field(default_factory=dict)


# 全局配置实例
_config = PaperTrailConfig()


def configure(**kwargs) -> None:
    """
    配置 PaperTrail 全局设置

    示例:
        configure(
            enabled=True,
            default_ignore_fields={'updated_at', 'modified_at'},
            batch_insert_threshold=50,
        )
    """
    global _config

    for key, value in kwargs.items():
        if hasattr(_config, key):
            setattr(_config, key, value)
        else:
            raise ValueError(f"Unknown configuration key: {key}")


def get_config() -> PaperTrailConfig:
    """获取当前配置"""
    return _config


def reset_config() -> None:
    """重置为默认配置"""
    global _config
    _config = PaperTrailConfig()
