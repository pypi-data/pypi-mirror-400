"""
版本恢复 (Reify)
~~~~~~~~~~~~~~~

从版本记录重建对象状态
"""

from typing import Any

from sqlalchemy.orm import Session

from .models import Version


def reify_version(
    session: Session,
    version: Version,
    model_class: type,
    commit: bool = False,
) -> Any:
    """
    从版本记录恢复对象

    参数:
        session: SQLAlchemy 会话
        version: 版本记录
        model_class: 目标模型类
        commit: 是否立即提交

    返回:
        恢复的模型实例

    示例:
        version = get_versions(session, Article, 123)[0]
        restored_article = reify_version(session, version, Article)
    """
    # 获取版本快照
    snapshot = version.object
    if not snapshot:
        raise ValueError(f"Version {version.id} has no object snapshot")

    # 查找现有对象
    obj = session.get(model_class, snapshot.get("id"))

    if obj is None:
        # 创建新对象（用于恢复已删除的记录）
        obj = model_class()

    # 恢复字段值
    for key, value in snapshot.items():
        if hasattr(obj, key) and key != "id":  # 不覆盖主键
            setattr(obj, key, value)

    session.add(obj)

    if commit:
        session.commit()
        session.refresh(obj)

    return obj


def reify_to_time(
    session: Session,
    model_class: type,
    model_id: Any,
    timestamp: Any,
) -> Any | None:
    """
    恢复对象到指定时间点的状态

    示例:
        article = reify_to_time(session, Article, 123, yesterday)
    """
    from datetime import datetime

    from .query import VersionQuery

    # 转换时间戳
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)

    # 查找最近的版本
    version = (
        VersionQuery(session)
        .for_model(model_class, model_id)
        .before(timestamp)
        .order_by_time(ascending=False)
        .first()
    )

    if not version:
        return None

    return reify_version(session, version, model_class, commit=False)


def get_changeset_diff(
    version_a: Version,
    version_b: Version,
) -> dict[str, tuple]:
    """
    比较两个版本的差异

    返回:
        {'field': (value_in_a, value_in_b)}
    """
    obj_a = version_a.object or {}
    obj_b = version_b.object or {}

    all_keys = set(obj_a.keys()) | set(obj_b.keys())
    diff = {}

    for key in all_keys:
        val_a = obj_a.get(key)
        val_b = obj_b.get(key)

        if val_a != val_b:
            diff[key] = (val_a, val_b)

    return diff
