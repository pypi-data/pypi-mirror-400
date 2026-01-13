"""
测试版本追踪装饰器
"""

from conftest import TestBase
from sqlalchemy import Column, Integer, String

from paper_trail import set_whodunnit, track_versions
from paper_trail.models import Version


@track_versions()
class Article(TestBase):
    __tablename__ = "articles"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    content = Column(String(1000))


class TestTrackVersions:
    """测试版本追踪装饰器"""

    def test_create_version_on_insert(self, session):
        """测试插入时创建版本"""
        # 创建新文章
        article = Article(title="Test Article", content="Test Content")
        session.add(article)
        session.commit()

        # 验证版本记录
        versions = (
            session.query(Version)
            .filter_by(item_type="articles", item_id=str(article.id))
            .all()
        )

        assert len(versions) == 1
        assert versions[0].event == "create"
        assert versions[0].object["title"] == "Test Article"

    def test_create_version_on_update(self, session):
        """测试更新时创建版本"""
        # 创建文章
        article = Article(title="Original", content="Content")
        session.add(article)
        session.commit()

        # 更新文章
        article.title = "Updated"
        session.commit()

        # 验证版本记录
        versions = (
            session.query(Version)
            .filter_by(item_type="articles", item_id=str(article.id))
            .order_by(Version.created_at)
            .all()
        )

        assert len(versions) == 2
        assert versions[1].event == "update"
        assert versions[1].changeset["title"] == ("Original", "Updated")

    def test_whodunnit_tracking(self, session):
        """测试操作者追踪"""
        set_whodunnit("user@example.com")

        article = Article(title="Test", content="Content")
        session.add(article)
        session.commit()

        version = session.query(Version).first()
        assert version.whodunnit == "user@example.com"

    def test_ignore_fields(self, session):
        """测试忽略字段"""
        from paper_trail import track_versions

        @track_versions(ignore={"content"})
        class Post(TestBase):
            __tablename__ = "posts"
            id = Column(Integer, primary_key=True)
            title = Column(String(200))
            content = Column(String(1000))

        # 创建表
        TestBase.metadata.create_all(session.bind)

        post = Post(title="Title", content="Content")
        session.add(post)
        session.commit()

        version = session.query(Version).filter_by(item_type="posts").first()
        assert "content" not in version.object
