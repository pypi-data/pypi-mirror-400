"""
测试配置和共享 fixtures
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from paper_trail.models import Base


class TestBase(DeclarativeBase):
    """测试模型的基类"""

    pass


@pytest.fixture(scope="session")
def engine():
    """创建测试数据库引擎"""
    # 使用 PostgreSQL 数据库（同步驱动 psycopg2）
    # 如果需要使用 asyncpg，需要改用异步测试框架
    database_url = (
        "postgresql+psycopg2://postgres:mlwkiRni@localhost:5432/paper_trail_test"
    )

    engine = create_engine(database_url, echo=False)

    # 创建版本表和测试表
    Base.metadata.create_all(engine)

    yield engine

    # 测试结束后清理
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """创建数据库会话"""
    # 清理所有表
    TestBase.metadata.drop_all(engine)
    Base.metadata.drop_all(engine)

    # 重新创建表
    Base.metadata.create_all(engine)
    TestBase.metadata.create_all(engine)

    # 创建事务连接
    connection = engine.connect()
    transaction = connection.begin()

    # 创建绑定到事务的 session
    Session = sessionmaker(bind=connection)
    session = Session()

    # 清理全局状态
    from paper_trail import decorators

    decorators._pending_versions = []

    yield session

    # 清理并回滚
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def clean_db(engine):
    """清理数据库"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    TestBase.metadata.drop_all(engine)
    TestBase.metadata.create_all(engine)
