"""
版本数据模型
~~~~~~~~~~~

存储所有模型变更的核心数据结构
"""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column, DateTime, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Version(Base):
    """版本记录模型"""

    __tablename__ = "versions"

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 追踪的对象信息
    item_type = Column(String(255), nullable=False, index=True)
    item_id = Column(String(255), nullable=False, index=True)

    # 事件类型: create, update, destroy
    event = Column(String(50), nullable=False, index=True)

    # 操作者
    whodunnit = Column(String(255), nullable=True, index=True)

    # 事务ID（用于分组关联的变更）
    transaction_id = Column(String(255), nullable=True, index=True)

    # 对象状态（完整快照）
    object = Column(JSON, nullable=True)

    # 仅变更的字段（增量）
    object_changes = Column(JSON, nullable=True)

    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # 复合索引优化查询
    __table_args__ = (
        Index("idx_item_lookup", "item_type", "item_id"),
        Index("idx_transaction_lookup", "transaction_id", "created_at"),
        Index("idx_whodunnit_lookup", "whodunnit", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<Version(id={self.id}, item={self.item_type}#{self.item_id}, "
            f"event={self.event}, by={self.whodunnit})>"
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典（用于数据库插入）"""
        return {
            "id": self.id,
            "item_type": self.item_type,
            "item_id": self.item_id,
            "event": self.event,
            "whodunnit": self.whodunnit,
            "transaction_id": self.transaction_id,
            "object": self.object,
            "object_changes": self.object_changes,
            "created_at": self.created_at,
        }

    @property
    def changeset(self) -> dict[str, tuple]:
        """
        获取变更集（字段 -> (旧值, 新值)）

        返回:
            {'title': ('Old Title', 'New Title')}
        """
        if not self.object_changes:
            return {}

        # 将 JSON 数组转换为元组
        result = {}
        for key, value in self.object_changes.items():
            # 如果值是列表（从 JSON 反序列化来的），转换为元组
            if isinstance(value, list) and len(value) == 2:
                result[key] = tuple(value)
            else:
                result[key] = value
        return result

    def reify(self) -> dict[str, Any]:
        """
        获取此版本对应的对象状态

        返回:
            对象的字段字典
        """
        return self.object or {}
