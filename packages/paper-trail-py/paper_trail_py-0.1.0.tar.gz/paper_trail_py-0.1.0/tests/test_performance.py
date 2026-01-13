"""
测试性能优化功能
"""

import pytest
from conftest import TestBase
from sqlalchemy import Column, Integer, String

from paper_trail import track_versions
from paper_trail.models import Version
from paper_trail.performance import bulk_track_changes, cleanup_old_versions


@track_versions()
class Article(TestBase):
    __tablename__ = "articles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    title = Column(String(200))


class TestPerformance:
    """测试性能优化"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        TestBase.metadata.create_all(session.bind)

    def test_bulk_track_changes(self, session):
        """测试批量追踪"""
        # 创建多个文章
        articles = []
        for i in range(10):
            article = Article(title=f"Article {i}")
            session.add(article)
            articles.append(article)

        session.commit()

        # 批量更新标题
        for article in articles:
            article.title = f"Updated {article.id}"

        # 批量追踪变更
        count = bulk_track_changes(
            session, articles, Article, event="update", whodunnit="batch@example.com"
        )

        session.commit()

        assert count == 10

        # 验证版本记录
        versions = session.query(Version).filter_by(event="update").all()
        assert len(versions) >= 10

    def test_cleanup_old_versions(self, session):
        """测试清理旧版本"""
        from datetime import datetime, timedelta

        # 创建一些文章
        for i in range(5):
            article = Article(title=f"Article {i}")
            session.add(article)
            session.commit()

        # 手动设置一些版本为旧版本
        old_date = datetime.utcnow() - timedelta(days=100)
        versions = session.query(Version).limit(3).all()
        for v in versions:
            v.created_at = old_date
        session.commit()

        # 清理 90 天前的版本
        deleted = cleanup_old_versions(session, days=90)

        assert deleted == 3
