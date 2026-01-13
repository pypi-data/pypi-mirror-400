"""
异步支持
~~~~~~~

为 SQLAlchemy 2.0+ 异步 API 提供版本追踪
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Version


class AsyncVersionQuery:
    """异步版本查询"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._query = select(Version)

    def for_model(self, model_class: type, model_id: Any) -> "AsyncVersionQuery":
        """查询特定模型的版本"""
        from sqlalchemy import and_

        self._query = self._query.where(
            and_(
                Version.item_type == model_class.__tablename__,
                Version.item_id == str(model_id),
            )
        )
        return self

    def by_user(self, user_id: str) -> "AsyncVersionQuery":
        """按用户过滤"""
        self._query = self._query.where(Version.whodunnit == user_id)
        return self

    def order_by_time(self, ascending: bool = False) -> "AsyncVersionQuery":
        """按时间排序"""
        from sqlalchemy import desc

        if ascending:
            self._query = self._query.order_by(Version.created_at)
        else:
            self._query = self._query.order_by(desc(Version.created_at))
        return self

    def limit(self, n: int) -> "AsyncVersionQuery":
        """限制结果数量"""
        self._query = self._query.limit(n)
        return self

    async def all(self) -> list[Version]:
        """执行查询并返回所有结果"""
        result = await self.session.execute(self._query)
        return list(result.scalars().all())

    async def first(self) -> Version | None:
        """返回第一个结果"""
        result = await self.session.execute(self._query.limit(1))
        return result.scalar_one_or_none()

    async def count(self) -> int:
        """返回结果数量"""
        from sqlalchemy import func

        count_query = select(func.count()).select_from(self._query.subquery())
        result = await self.session.execute(count_query)
        return result.scalar_one()


async def get_versions_async(
    session: AsyncSession,
    model_class: type,
    model_id: Any,
    limit: int | None = None,
) -> list[Version]:
    """
    异步获取版本历史

    示例:
        versions = await get_versions_async(session, Article, 123)
    """
    query = AsyncVersionQuery(session).for_model(model_class, model_id)
    query = query.order_by_time(ascending=False)

    if limit:
        query = query.limit(limit)

    return await query.all()


async def reify_version_async(
    session: AsyncSession,
    version: Version,
    model_class: type,
    commit: bool = False,
) -> Any:
    """
    异步恢复版本

    示例:
        restored = await reify_version_async(session, version, Article)
    """
    snapshot = version.object
    if not snapshot:
        raise ValueError(f"Version {version.id} has no object snapshot")

    # 查找现有对象
    obj = await session.get(model_class, snapshot.get("id"))

    if obj is None:
        obj = model_class()

    # 恢复字段
    for key, value in snapshot.items():
        if hasattr(obj, key) and key != "id":
            setattr(obj, key, value)

    session.add(obj)

    if commit:
        await session.commit()
        await session.refresh(obj)

    return obj
