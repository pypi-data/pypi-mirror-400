"""
数据库模块
提供 PostgreSQL 数据库连接、会话管理、ORM 基类和迁移功能
"""

from .client import (
    Base,
    get_db_url,
    get_engine,
    get_session,
    get_sessionmaker,
)
from .migration import (
    generate_models,
    upgrade,
)

__all__ = [
    # ORM 基类
    "Base",
    # 数据库连接
    "get_db_url",
    "get_engine",
    "get_session",
    "get_sessionmaker",
    # 迁移功能
    "generate_models",
    "upgrade",
]
