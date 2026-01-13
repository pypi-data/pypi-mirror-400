"""
上下文管理
~~~~~~~~~

管理 whodunnit（操作者）和事务分组
"""

import contextvars
import uuid
from contextlib import contextmanager

# 线程安全的上下文变量
_whodunnit_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "whodunnit", default=None
)

_transaction_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "transaction_id", default=None
)


def set_whodunnit(user_id: str | None) -> None:
    """
    设置当前操作者

    参数:
        user_id: 用户标识（ID、邮箱等）

    示例:
        set_whodunnit('user@example.com')
        article.title = 'New Title'
        session.commit()  # 版本记录会包含 whodunnit
    """
    _whodunnit_var.set(user_id)


def get_whodunnit() -> str | None:
    """获取当前操作者"""
    return _whodunnit_var.get()


@contextmanager
def whodunnit(user_id: str):
    """
    上下文管理器：临时设置操作者

    示例:
        with whodunnit('admin@example.com'):
            article.title = 'Admin Update'
            session.commit()
    """
    token = _whodunnit_var.set(user_id)
    try:
        yield
    finally:
        _whodunnit_var.reset(token)


def set_transaction_id(transaction_id: str | None) -> None:
    """设置事务ID"""
    _transaction_id_var.set(transaction_id)


def get_transaction_id() -> str | None:
    """获取当前事务ID"""
    return _transaction_id_var.get()


@contextmanager
def transaction_group():
    """
    上下文管理器：将多个变更分组到一个事务

    示例:
        with transaction_group():
            article.title = 'New Title'
            article.content = 'New Content'
            session.commit()
            # 两个版本记录会有相同的 transaction_id
    """
    transaction_id = str(uuid.uuid4())
    token = _transaction_id_var.set(transaction_id)
    try:
        yield transaction_id
    finally:
        _transaction_id_var.reset(token)
