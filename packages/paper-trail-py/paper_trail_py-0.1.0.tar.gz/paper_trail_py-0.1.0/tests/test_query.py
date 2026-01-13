"""
测试版本查询 API
"""

import pytest
from conftest import TestBase
from sqlalchemy import Column, Integer, String

from paper_trail import VersionQuery, track_versions


@track_versions()
class Article(TestBase):
    __tablename__ = "articles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    title = Column(String(200))


class TestVersionQuery:
    """测试版本查询"""

    @pytest.fixture(autouse=True)
    def setup_data(self, session):
        """创建测试数据"""
        TestBase.metadata.create_all(session.bind)

        # 创建多个文章和版本
        for i in range(3):
            article = Article(title=f"Article {i}")
            session.add(article)
            session.commit()

            article.title = f"Updated {i}"
            session.commit()

    def test_for_model(self, session):
        """测试按模型查询"""
        article = session.query(Article).first()

        versions = VersionQuery(session).for_model(Article, article.id).all()

        assert len(versions) == 2  # create + update
        assert all(v.item_id == str(article.id) for v in versions)

    def test_for_model_type(self, session):
        """测试按模型类型查询"""
        versions = VersionQuery(session).for_model_type(Article).all()

        assert len(versions) == 6  # 3 articles * 2 events each

    def test_by_event(self, session):
        """测试按事件类型过滤"""
        create_versions = VersionQuery(session).by_event("create").all()
        update_versions = VersionQuery(session).by_event("update").all()

        assert len(create_versions) == 3
        assert len(update_versions) == 3

    def test_order_by_time(self, session):
        """测试时间排序"""
        versions_desc = VersionQuery(session).order_by_time(ascending=False).all()

        versions_asc = VersionQuery(session).order_by_time(ascending=True).all()

        assert versions_desc[0].created_at >= versions_desc[-1].created_at
        assert versions_asc[0].created_at <= versions_asc[-1].created_at

    def test_limit(self, session):
        """测试限制结果数量"""
        versions = VersionQuery(session).limit(2).all()

        assert len(versions) == 2

    def test_count(self, session):
        """测试计数"""
        count = VersionQuery(session).count()

        assert count == 6
