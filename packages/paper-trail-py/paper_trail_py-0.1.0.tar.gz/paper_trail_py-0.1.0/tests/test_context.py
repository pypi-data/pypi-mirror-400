"""
测试上下文管理
"""

import pytest
from conftest import TestBase
from sqlalchemy import Column, Integer, String

from paper_trail import get_whodunnit, set_whodunnit, track_versions
from paper_trail.context import transaction_group, whodunnit
from paper_trail.models import Version


@track_versions()
class Article(TestBase):
    __tablename__ = "articles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    title = Column(String(200))


class TestContext:
    """测试上下文管理"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        TestBase.metadata.create_all(session.bind)

    def test_whodunnit_context_manager(self, session):
        """测试 whodunnit 上下文管理器"""
        with whodunnit("user1@example.com"):
            article1 = Article(title="Article 1")
            session.add(article1)
            session.commit()

        with whodunnit("user2@example.com"):
            article2 = Article(title="Article 2")
            session.add(article2)
            session.commit()

        versions = session.query(Version).order_by(Version.id).all()

        assert versions[0].whodunnit == "user1@example.com"
        assert versions[1].whodunnit == "user2@example.com"

    def test_transaction_group(self, session):
        """测试事务分组"""
        with transaction_group() as tx_id:
            article = Article(title="Article")
            session.add(article)
            session.commit()

            article.title = "Updated"
            session.commit()

        versions = session.query(Version).all()

        assert len(versions) == 2
        assert versions[0].transaction_id == tx_id
        assert versions[1].transaction_id == tx_id

    def test_set_get_whodunnit(self):
        """测试设置和获取 whodunnit"""
        set_whodunnit("test@example.com")
        assert get_whodunnit() == "test@example.com"

        set_whodunnit(None)
        assert get_whodunnit() is None
