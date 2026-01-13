"""
版本追踪装饰器
~~~~~~~~~~~~~

为 SQLAlchemy 模型提供自动版本追踪功能
"""

from datetime import datetime

from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase, Session

from .context import get_transaction_id, get_whodunnit
from .models import Version
from .serializers import DefaultSerializer, Serializer

# 用于存储待创建的版本信息
_pending_versions = []


def track_versions(
    *,
    only: set[str] | None = None,
    ignore: set[str] | None = None,
    serializer: Serializer | None = None,
):
    """
    装饰器：为模型启用版本追踪

    参数:
        only: 仅追踪这些字段的变化
        ignore: 忽略这些字段的变化
        serializer: 自定义序列化器

    示例:
        @track_versions(ignore={'updated_at'})
        class Article(Base):
            __tablename__ = 'articles'
            id = Column(Integer, primary_key=True)
            title = Column(String)
            content = Column(Text)
    """

    def decorator(cls: type[DeclarativeBase]) -> type[DeclarativeBase]:
        # 保存配置到类属性
        cls.__paper_trail_config__ = {
            "only": only,
            "ignore": ignore or {"updated_at", "modified_at"},
            "serializer": serializer or DefaultSerializer(),
        }

        # 标记此类已被追踪
        cls.__paper_trail_tracked__ = True

        return cls

    return decorator


# 注册全局 session 事件监听器
@event.listens_for(Session, "before_flush")
def receive_before_flush(session, _flush_context, _instances):
    """在 flush 之前收集需要创建的版本信息"""
    global _pending_versions

    for obj in session.new:
        if hasattr(obj, "__paper_trail_tracked__"):
            config = obj.__paper_trail_config__
            _pending_versions.append(
                {
                    "item_type": obj.__tablename__,
                    "item_id": None,  # 新对象还没有 ID
                    "event": "create",
                    "object": config["serializer"].serialize(obj, config),
                    "object_changes": None,
                    "obj": obj,  # 保存引用以便后续获取 ID
                }
            )

    for obj in session.dirty:
        if hasattr(obj, "__paper_trail_tracked__") and session.is_modified(obj):
            config = obj.__paper_trail_config__
            serializer = config["serializer"]

            # 收集变更
            changes = serializer.get_changes(obj, config)
            # 即使没有检测到变更，只要对象被修改了，也创建版本记录
            # 这样可以记录被忽略字段之外的所有变更
            _pending_versions.append(
                {
                    "item_type": obj.__tablename__,
                    "item_id": str(obj.id),
                    "event": "update",
                    "object": serializer.serialize(obj, config),
                    "object_changes": changes,
                    "obj": None,
                }
            )

    for obj in session.deleted:
        if hasattr(obj, "__paper_trail_tracked__"):
            config = obj.__paper_trail_config__
            _pending_versions.append(
                {
                    "item_type": obj.__tablename__,
                    "item_id": str(obj.id),
                    "event": "destroy",
                    "object": config["serializer"].serialize(obj, config),
                    "object_changes": None,
                    "obj": None,
                }
            )


@event.listens_for(Session, "after_flush_postexec")
def receive_after_flush(session, _flush_context):
    """在 flush 完成后创建版本记录"""
    global _pending_versions

    if not _pending_versions:
        return

    # 收集所有待创建的版本
    versions_to_create = []

    for version_data in _pending_versions:
        # 对于新创建的对象，现在获取其 ID
        if version_data["obj"] is not None:
            version_data["item_id"] = str(version_data["obj"].id)
            version_data.pop("obj")

        version = Version(
            item_type=version_data["item_type"],
            item_id=version_data["item_id"],
            event=version_data["event"],
            object=version_data["object"],
            object_changes=version_data["object_changes"],
            whodunnit=get_whodunnit(),
            transaction_id=get_transaction_id(),
            created_at=datetime.utcnow(),
        )

        versions_to_create.append(version)

    # 清空待处理列表
    _pending_versions = []

    # 批量添加所有版本记录
    session.add_all(versions_to_create)
