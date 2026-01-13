"""
序列化器
~~~~~~~

处理对象快照和变更检测
"""

from typing import Any, Protocol

from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase


class Serializer(Protocol):
    """序列化器接口"""

    def serialize(
        self,
        obj: DeclarativeBase,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """将对象序列化为字典"""
        ...

    def get_changes(
        self,
        obj: DeclarativeBase,
        config: dict[str, Any],
    ) -> dict[str, tuple] | None:
        """获取对象的变更"""
        ...


class DefaultSerializer:
    """默认序列化器"""

    def serialize(
        self,
        obj: DeclarativeBase,
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """
        序列化对象为 JSON 兼容的字典

        参数:
            obj: SQLAlchemy 模型实例
            config: 追踪配置（only, ignore）
        """
        inspector = inspect(obj)
        result = {}

        only = config.get("only")
        ignore = config.get("ignore", set())

        for column in inspector.mapper.column_attrs:
            key = column.key

            # 应用过滤规则
            if only and key not in only:
                continue
            if key in ignore:
                continue

            value = getattr(obj, key)

            # 处理特殊类型
            result[key] = self._serialize_value(value)

        return result

    def get_changes(
        self,
        obj: DeclarativeBase,
        config: dict[str, Any],
    ) -> dict[str, tuple] | None:
        """
        检测对象的变更

        返回:
            {'field': (old_value, new_value)} 或 None（无变更）
        """
        from sqlalchemy import inspect as sa_inspect
        from sqlalchemy.orm import object_session

        inspector = sa_inspect(obj)
        changes = {}

        only = config.get("only")
        ignore = config.get("ignore", set())

        # 获取当前 session
        session = object_session(obj)
        if not session:
            return None

        # 获取对象的主键
        pk_attrs = inspector.mapper.primary_key
        pk_values = [getattr(obj, pk.name) for pk in pk_attrs]

        # 如果对象是新的（没有主键），无法获取旧值
        if any(v is None for v in pk_values):
            return None

        # 从数据库重新加载对象的当前状态（未刷新的）
        # 使用原始 SQL 查询避免 identity map 的影响
        from sqlalchemy import select

        with session.no_autoflush:
            # 使用 select() 和表对象构造查询
            table = inspector.mapper.persist_selectable
            stmt = select(table).where(
                *[
                    table.c[pk.name] == pk_val
                    for pk, pk_val in zip(pk_attrs, pk_values, strict=True)
                ]
            )
            result = session.execute(stmt).first()

        # 比较内存中的值和数据库中的值
        for attr in inspector.mapper.column_attrs:
            key = attr.key

            # 应用过滤规则
            if only and key not in only:
                continue
            if key in ignore:
                continue

            # 获取新值（内存中的）
            new_value = self._serialize_value(getattr(obj, key))

            # 获取旧值（数据库中的）
            old_value = self._serialize_value(getattr(result, key)) if result else None

            # 只记录真正有变化的字段
            if old_value != new_value:
                changes[key] = (old_value, new_value)

        return changes if changes else None

    def _serialize_value(self, value: Any) -> Any:
        """序列化单个值"""
        from datetime import date, datetime
        from decimal import Decimal
        from enum import Enum

        if value is None:
            return None

        if isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, Decimal):
            return float(value)

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, (list, tuple)):
            return [self._serialize_value(v) for v in value]

        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}

        # 回退到字符串
        return str(value)


class CustomFieldSerializer(DefaultSerializer):
    """
    支持自定义字段序列化

    示例:
        serializer = CustomFieldSerializer(
            custom_fields={
                'price': lambda v: f"${v:.2f}",
                'tags': lambda v: ','.join(v),
            }
        )
    """

    def __init__(self, custom_fields: dict[str, callable]):
        self.custom_fields = custom_fields

    def _serialize_value(self, value: Any, field_name: str | None = None) -> Any:
        if field_name and field_name in self.custom_fields:
            return self.custom_fields[field_name](value)

        return super()._serialize_value(value)
