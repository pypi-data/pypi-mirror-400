"""
测试版本恢复功能
"""

import pytest
from conftest import TestBase
from sqlalchemy import Column, Integer, String

from paper_trail import track_versions
from paper_trail.query import get_versions
from paper_trail.reify import get_changeset_diff, reify_version


@track_versions()
class Article(TestBase):
    __tablename__ = "articles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(String(1000))


class TestReify:
    """测试版本恢复"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        TestBase.metadata.create_all(session.bind)

    def test_reify_version(self, session):
        """测试恢复到指定版本"""
        # 创建并修改文章
        article = Article(title="Original", content="Original Content")
        session.add(article)
        session.commit()

        article.title = "Updated"
        session.commit()

        # 获取第一个版本（创建时）
        versions = get_versions(session, Article, article.id)
        original_version = versions[-1]  # 最早的版本

        # 恢复
        restored = reify_version(session, original_version, Article, commit=True)

        assert restored.title == "Original"
        assert restored.content == "Original Content"

    def test_changeset_diff(self, session):
        """测试版本差异比较"""
        article = Article(title="V1", content="Content V1")
        session.add(article)
        session.commit()

        article.title = "V2"
        article.content = "Content V2"
        session.commit()

        # 获取两个版本
        versions = get_versions(session, Article, article.id)

        diff = get_changeset_diff(versions[1], versions[0])

        assert "title" in diff
        assert diff["title"] == ("V1", "V2")
        assert "content" in diff
