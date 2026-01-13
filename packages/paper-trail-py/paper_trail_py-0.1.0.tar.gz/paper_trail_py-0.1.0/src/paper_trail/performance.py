"""
性能优化
~~~~~~~

批量操作和性能增强
"""

from sqlalchemy import insert
from sqlalchemy.orm import Session

from .context import get_whodunnit
from .models import Version


class BatchVersionCreator:
    """批量创建版本记录"""

    def __init__(self, session: Session, batch_size: int = 100):
        self.session = session
        self.batch_size = batch_size
        self._buffer: list[dict] = []

    def add_version(self, version_data: dict) -> None:
        """添加版本到缓冲区"""
        self._buffer.append(version_data)

        if len(self._buffer) >= self.batch_size:
            self.flush()

    def flush(self) -> None:
        """立即提交缓冲区的所有版本"""
        if not self._buffer:
            return

        # 批量插入
        self.session.execute(insert(Version), self._buffer)

        self._buffer.clear()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.flush()


def bulk_track_changes(
    session: Session,
    items: list,
    model_class: type,
    event: str = "update",
    whodunnit: str = None,
) -> int:
    """
    批量追踪多个对象的变更

    参数:
        session: SQLAlchemy 会话
        items: 模型实例列表
        model_class: 模型类
        event: 事件类型
        whodunnit: 操作者

    返回:
        创建的版本记录数量

    示例:
        articles = session.query(Article).filter(...).all()
        count = bulk_track_changes(session, articles, Article, 'update')
    """
    from .context import get_transaction_id
    from .serializers import DefaultSerializer

    serializer = DefaultSerializer()
    config = getattr(
        model_class,
        "__paper_trail_config__",
        {
            "only": None,
            "ignore": {"updated_at", "modified_at"},
            "serializer": serializer,
        },
    )

    with BatchVersionCreator(session) as batch:
        for item in items:
            version_data = {
                "item_type": model_class.__tablename__,
                "item_id": str(item.id),
                "event": event,
                "object": serializer.serialize(item, config),
                "whodunnit": whodunnit or get_whodunnit(),
                "transaction_id": get_transaction_id(),
            }

            batch.add_version(version_data)

    return len(items)


def cleanup_old_versions(
    session: Session,
    days: int = 90,
    model_class: type = None,
) -> int:
    """
    清理旧版本记录

    参数:
        session: SQLAlchemy 会话
        days: 保留天数
        model_class: 仅清理特定模型的版本

    返回:
        删除的记录数

    示例:
        deleted = cleanup_old_versions(session, days=30, model_class=Article)
    """
    from datetime import datetime, timedelta

    from sqlalchemy import delete

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    query = delete(Version).where(Version.created_at < cutoff_date)

    if model_class:
        query = query.where(Version.item_type == model_class.__tablename__)

    result = session.execute(query)
    session.commit()

    return result.rowcount
