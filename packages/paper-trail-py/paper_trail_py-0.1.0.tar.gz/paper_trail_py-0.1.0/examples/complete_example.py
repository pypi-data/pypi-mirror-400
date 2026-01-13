"""
使用示例：完整演示 PaperTrail 的所有功能
"""

from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from paper_trail import (
    VersionQuery,
    configure,
    reify_version,
    set_whodunnit,
    track_versions,
    whodunnit,
)
from paper_trail.context import transaction_group
from paper_trail.performance import bulk_track_changes, cleanup_old_versions

# ==================== 1. 定义模型 ====================


class Base(DeclarativeBase):
    pass


@track_versions()
class Article(Base):
    """文章模型 - 启用完整版本追踪"""

    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    status = Column(String(20), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


@track_versions(ignore={"view_count", "updated_at"})
class Page(Base):
    """页面模型 - 忽略特定字段"""

    __tablename__ = "pages"

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    slug = Column(String(100))
    view_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)


# ==================== 2. 初始化数据库 ====================


def setup_database():
    """创建数据库和表"""
    engine = create_engine("sqlite:///example.db", echo=True)
    Base.metadata.create_all(engine)
    return engine


# ==================== 3. 基础使用 ====================


def example_basic_usage(session: Session):
    """示例：基础版本追踪"""
    print("\n=== 基础版本追踪 ===")

    # 设置操作者
    set_whodunnit("john@example.com")

    # 创建文章
    article = Article(
        title="Getting Started with PaperTrail",
        content="This is a tutorial...",
        status="draft",
    )
    session.add(article)
    session.commit()
    print(f"✅ 创建文章: {article.title}")

    # 更新文章
    article.title = "Getting Started with PaperTrail (Updated)"
    article.status = "published"
    session.commit()
    print(f"✅ 更新文章: {article.title}")

    # 查询版本历史
    versions = (
        VersionQuery(session)
        .for_model(Article, article.id)
        .order_by_time(ascending=False)
        .all()
    )

    print(f"\n📚 版本历史 ({len(versions)} 条记录):")
    for v in versions:
        print(f"  - {v.event} by {v.whodunnit} at {v.created_at}")
        if v.object_changes:
            print(f"    Changes: {v.object_changes}")

    return article


# ==================== 4. 上下文管理 ====================


def example_context_manager(session: Session, article: Article):
    """示例：使用上下文管理器"""
    print("\n=== 上下文管理器 ===")

    # 临时切换操作者
    with whodunnit("admin@example.com"):
        article.content = "Content updated by admin"
        session.commit()
        print("✅ 管理员更新内容")

    # 恢复原操作者
    article.title = "Title updated by original user"
    session.commit()
    print("✅ 原用户更新标题")

    # 查看最近两次操作的操作者
    recent_versions = (
        VersionQuery(session)
        .for_model(Article, article.id)
        .order_by_time(ascending=False)
        .limit(2)
        .all()
    )

    print("\n👤 最近两次操作者:")
    for v in recent_versions:
        print(f"  - {v.whodunnit}: {v.event}")


# ==================== 5. 事务分组 ====================


def example_transaction_group(session: Session):
    """示例：事务分组"""
    print("\n=== 事务分组 ===")

    with transaction_group() as tx_id:
        print(f"🔗 事务 ID: {tx_id}")

        # 批量创建和修改
        article1 = Article(title="Article 1", content="Content 1")
        article2 = Article(title="Article 2", content="Content 2")
        session.add_all([article1, article2])
        session.commit()

        article1.status = "published"
        article2.status = "published"
        session.commit()

        print("✅ 批量操作完成")

    # 查询事务内的所有变更
    tx_versions = VersionQuery(session).by_transaction(tx_id).all()

    print(f"\n📦 事务内的变更 ({len(tx_versions)} 条):")
    for v in tx_versions:
        print(f"  - {v.item_type}#{v.item_id}: {v.event}")


# ==================== 6. 版本恢复 ====================


def example_reify(session: Session, article: Article):
    """示例：版本恢复"""
    print("\n=== 版本恢复 ===")

    # 获取历史版本
    versions = (
        VersionQuery(session)
        .for_model(Article, article.id)
        .order_by_time(ascending=False)
        .all()
    )

    if len(versions) >= 2:
        # 显示当前状态
        print(f"当前标题: {article.title}")

        # 恢复到上一个版本
        previous_version = versions[1]
        print(f"\n⏮️  恢复到版本 #{previous_version.id}")

        restored = reify_version(session, previous_version, Article, commit=True)
        print(f"恢复后标题: {restored.title}")
    else:
        print("版本记录不足，跳过恢复示例")


# ==================== 7. 高级查询 ====================


def example_advanced_queries(session: Session):
    """示例：高级查询"""
    print("\n=== 高级查询 ===")

    # 查询所有文章的版本
    all_article_versions = VersionQuery(session).for_model_type(Article).count()
    print(f"📊 文章版本总数: {all_article_versions}")

    # 查询特定用户的操作
    user_versions = VersionQuery(session).by_user("john@example.com").all()
    print(f"👤 john@example.com 的操作: {len(user_versions)} 条")

    # 查询最近 24 小时的变更
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_versions = VersionQuery(session).after(yesterday).by_event("update").all()
    print(f"🕐 最近 24 小时的更新: {len(recent_versions)} 条")


# ==================== 8. 性能优化 ====================


def example_performance(session: Session):
    """示例：性能优化"""
    print("\n=== 性能优化 ===")

    # 创建一批文章
    articles = []
    for i in range(10):
        article = Article(
            title=f"Bulk Article {i}",
            content=f"Content {i}",
        )
        session.add(article)
        articles.append(article)
    session.commit()
    print(f"✅ 创建了 {len(articles)} 篇文章")

    # 批量修改
    for article in articles:
        article.status = "published"

    # 批量追踪变更
    count = bulk_track_changes(
        session, articles, Article, event="update", whodunnit="batch@example.com"
    )
    session.commit()
    print(f"⚡ 批量追踪了 {count} 条变更")

    # 清理旧版本（这里演示，实际不会删除因为都是新创建的）
    deleted = cleanup_old_versions(session, days=365)
    print(f"🗑️  清理了 {deleted} 条旧版本")


# ==================== 9. 配置管理 ====================


def example_configuration():
    """示例：全局配置"""
    print("\n=== 全局配置 ===")

    configure(
        enabled=True,
        default_ignore_fields={"updated_at", "view_count"},
        store_object_snapshot=True,
        store_object_changes=True,
        batch_insert_threshold=50,
    )
    print("✅ 配置已更新")


# ==================== 10. 完整示例 ====================


def main():
    """运行所有示例"""
    print("🚀 PaperTrail 完整示例")
    print("=" * 60)

    # 配置
    example_configuration()

    # 初始化数据库
    engine = setup_database()
    session = Session(engine)

    try:
        # 基础使用
        article = example_basic_usage(session)

        # 上下文管理
        example_context_manager(session, article)

        # 事务分组
        example_transaction_group(session)

        # 版本恢复
        example_reify(session, article)

        # 高级查询
        example_advanced_queries(session)

        # 性能优化
        example_performance(session)

        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成！")

    finally:
        session.close()


if __name__ == "__main__":
    main()
