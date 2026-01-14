"""
数据库连接模块
提供 PostgreSQL 数据库连接、会话管理和 ORM 基类
"""

import os
import time
import logging
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

MAX_RETRY_TIME = 20  # 连接最大重试时间（秒）

_engine: Optional[Engine] = None
_SessionLocal = None


class Base(DeclarativeBase):
    """SQLAlchemy ORM 模型基类"""

    pass


def _load_env() -> None:
    """加载环境变量（内部使用）"""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass


def get_db_url() -> str:
    """
    获取数据库连接 URL

    优先从环境变量 PGDATABASE_URL 获取，
    如果不存在则尝试从 coze_workload_identity 获取。

    Returns:
        str: 数据库连接 URL

    Raises:
        ValueError: 如果无法获取数据库 URL
    """
    _load_env()

    url = os.getenv("PGDATABASE_URL") or ""
    if url:
        return url

    try:
        from coze_workload_identity import Client

        client = Client()
        env_vars = client.get_project_env_vars()
        client.close()
        for env_var in env_vars:
            if env_var.key == "PGDATABASE_URL":
                url = env_var.value.replace("'", "'\\''")
                return url
    except Exception as e:
        logger.error(f"Error loading PGDATABASE_URL: {e}")
        raise e

    if not url:
        logger.error("PGDATABASE_URL is not set")
        raise ValueError("PGDATABASE_URL is not set")

    return url


def _create_engine_with_retry() -> Engine:
    """创建数据库引擎（带重试）"""
    url = get_db_url()
    if not url:
        logger.error("PGDATABASE_URL is not set")
        raise ValueError("PGDATABASE_URL is not set")

    size = 100
    overflow = 100
    recycle = 1800
    timeout = 30

    engine = create_engine(
        url,
        pool_size=size,
        max_overflow=overflow,
        pool_pre_ping=True,
        pool_recycle=recycle,
        pool_timeout=timeout,
    )

    # 验证连接，带重试
    start_time = time.time()
    last_error = None
    while time.time() - start_time < MAX_RETRY_TIME:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except OperationalError as e:
            last_error = e
            elapsed = time.time() - start_time
            logger.warning(f"Database connection failed, retrying... (elapsed: {elapsed:.1f}s)")
            time.sleep(min(1, MAX_RETRY_TIME - elapsed))

    logger.error(f"Database connection failed after {MAX_RETRY_TIME}s: {last_error}")
    raise last_error


def get_engine() -> Engine:
    """
    获取数据库引擎（单例）

    Returns:
        Engine: SQLAlchemy 数据库引擎
    """
    global _engine
    if _engine is None:
        _engine = _create_engine_with_retry()
    return _engine


def get_sessionmaker():
    """
    获取 sessionmaker（单例）

    Returns:
        sessionmaker: SQLAlchemy sessionmaker
    """
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_session() -> Session:
    """
    创建新的数据库会话

    Returns:
        Session: SQLAlchemy 会话实例

    Example:
        >>> from coze_coding_dev_sdk.database import get_session
        >>> db = get_session()
        >>> try:
        ...     # 执行数据库操作
        ...     pass
        ... finally:
        ...     db.close()
    """
    return get_sessionmaker()()


__all__ = [
    "Base",
    "get_db_url",
    "get_engine",
    "get_sessionmaker",
    "get_session",
]
