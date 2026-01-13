"""
版本查询 API
~~~~~~~~~~~

提供丰富的版本查询接口
"""

from datetime import datetime
from typing import Any

from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from .models import Version


class VersionQuery:
    """版本查询构建器"""

    def __init__(self, session: Session):
        self.session = session
        self._query = select(Version)

    def for_model(self, model_class: type, model_id: Any) -> "VersionQuery":
        """
        查询特定模型实例的版本

        示例:
            query.for_model(Article, 123)
        """
        self._query = self._query.where(
            and_(
                Version.item_type == model_class.__tablename__,
                Version.item_id == str(model_id),
            )
        )
        return self

    def for_model_type(self, model_class: type) -> "VersionQuery":
        """
        查询特定模型类型的所有版本

        示例:
            query.for_model_type(Article)
        """
        self._query = self._query.where(Version.item_type == model_class.__tablename__)
        return self

    def by_user(self, user_id: str) -> "VersionQuery":
        """
        查询特定用户的操作

        示例:
            query.by_user('user@example.com')
        """
        self._query = self._query.where(Version.whodunnit == user_id)
        return self

    def by_transaction(self, transaction_id: str) -> "VersionQuery":
        """
        查询特定事务的所有变更

        示例:
            query.by_transaction('uuid-xxx')
        """
        self._query = self._query.where(Version.transaction_id == transaction_id)
        return self

    def by_event(self, event: str) -> "VersionQuery":
        """
        按事件类型过滤

        参数:
            event: 'create', 'update', 'destroy'
        """
        self._query = self._query.where(Version.event == event)
        return self

    def between(self, start: datetime, end: datetime) -> "VersionQuery":
        """
        时间范围过滤

        示例:
            query.between(yesterday, today)
        """
        self._query = self._query.where(
            and_(Version.created_at >= start, Version.created_at <= end)
        )
        return self

    def after(self, timestamp: datetime) -> "VersionQuery":
        """在指定时间之后"""
        self._query = self._query.where(Version.created_at > timestamp)
        return self

    def before(self, timestamp: datetime) -> "VersionQuery":
        """在指定时间之前"""
        self._query = self._query.where(Version.created_at < timestamp)
        return self

    def order_by_time(self, ascending: bool = False) -> "VersionQuery":
        """按时间排序"""
        if ascending:
            self._query = self._query.order_by(Version.created_at)
        else:
            self._query = self._query.order_by(desc(Version.created_at))
        return self

    def limit(self, n: int) -> "VersionQuery":
        """限制结果数量"""
        self._query = self._query.limit(n)
        return self

    def all(self) -> list[Version]:
        """执行查询并返回所有结果"""
        result = self.session.execute(self._query)
        return list(result.scalars().all())

    def first(self) -> Version | None:
        """返回第一个结果"""
        result = self.session.execute(self._query.limit(1))
        return result.scalar_one_or_none()

    def count(self) -> int:
        """返回结果数量"""
        from sqlalchemy import func

        count_query = select(func.count()).select_from(self._query.subquery())
        result = self.session.execute(count_query)
        return result.scalar_one()


def get_versions(
    session: Session,
    model_class: type,
    model_id: Any,
    limit: int | None = None,
) -> list[Version]:
    """
    快捷方法：获取模型的版本历史

    示例:
        versions = get_versions(session, Article, 123, limit=10)
    """
    query = VersionQuery(session).for_model(model_class, model_id)
    query = query.order_by_time(ascending=False)

    if limit:
        query = query.limit(limit)

    return query.all()
