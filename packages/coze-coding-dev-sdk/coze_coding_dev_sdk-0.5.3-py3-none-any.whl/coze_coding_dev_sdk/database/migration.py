"""
数据库迁移模块
提供 Alembic 迁移功能的 Python API 封装
"""

import os
import sys
import tempfile
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Alembic script.py.mako 模板
SCRIPT_MAKO_TEMPLATE = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
'''

# 全局缓存的 alembic 目录
_alembic_dir: Optional[str] = None


def _load_env() -> None:
    """加载环境变量"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    try:
        from coze_workload_identity import Client
        client = Client()
        env_vars = client.get_project_env_vars()
        client.close()
        for env_var in env_vars:
            if env_var.key not in os.environ:
                os.environ[env_var.key] = env_var.value
    except Exception as e:
        logger.debug(f"coze_workload_identity not available: {e}")


def _get_db_url() -> str:
    """获取数据库 URL"""
    _load_env()

    url = os.getenv("PGDATABASE_URL")
    if url:
        # 兼容 postgres:// 前缀
        if url.startswith("postgres://"):
            url = "postgresql://" + url[len("postgres://"):]
        return url

    raise ValueError(
        "Database URL not configured. Set PGDATABASE_URL environment variable.\n"
        "Did you create a database? You can create one via the Coze Coding platform."
    )


def _get_alembic_dir() -> str:
    """获取或创建 alembic 临时目录"""
    global _alembic_dir
    if _alembic_dir and os.path.exists(_alembic_dir):
        return _alembic_dir

    # 使用固定的临时目录，避免每次创建新目录
    _alembic_dir = os.path.join(tempfile.gettempdir(), "coze_sdk_alembic")
    os.makedirs(_alembic_dir, exist_ok=True)
    os.makedirs(os.path.join(_alembic_dir, "versions"), exist_ok=True)
    return _alembic_dir


def _ensure_alembic_env(model_import_path: str) -> str:
    """
    确保 alembic 环境已初始化

    Args:
        model_import_path: 模型导入路径，如 "storage.database.shared.model"

    Returns:
        str: alembic 脚本目录路径
    """
    script_location = _get_alembic_dir()

    # 创建 env.py（支持 -x 参数传递 version_table 和 version_table_schema）
    env_py_content = f'''"""Alembic Environment Configuration (Auto-generated)"""

import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name)

# 获取 -x 参数
x_args = context.get_x_argument(as_dictionary=True)
version_table = x_args.get("version_table")
version_table_schema = x_args.get("version_table_schema")

# 导入 Base
from coze_coding_dev_sdk.database import Base

# 导入用户模型以注册到 metadata
from {model_import_path} import *

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    kwargs = {{
        "url": url,
        "target_metadata": target_metadata,
        "literal_binds": True,
        "compare_type": True,
        "compare_server_default": True,
        "compare_nullable": True,
    }}
    if version_table:
        kwargs["version_table"] = version_table
    if version_table_schema:
        kwargs["version_table_schema"] = version_table_schema
    context.configure(**kwargs)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        kwargs = {{
            "connection": connection,
            "target_metadata": target_metadata,
            "compare_type": True,
            "compare_server_default": True,
            "compare_nullable": True,
        }}
        if version_table:
            kwargs["version_table"] = version_table
        if version_table_schema:
            kwargs["version_table_schema"] = version_table_schema
        context.configure(**kwargs)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

    env_py_path = os.path.join(script_location, "env.py")
    with open(env_py_path, "w") as f:
        f.write(env_py_content)

    # 创建 script.py.mako
    mako_path = os.path.join(script_location, "script.py.mako")
    with open(mako_path, "w") as f:
        f.write(SCRIPT_MAKO_TEMPLATE)

    return script_location


def _get_alembic_config(model_import_path: str, model_path: Optional[str] = None):
    """
    创建 Alembic 配置对象

    Args:
        model_import_path: 模型导入路径
        model_path: 模型文件所在目录（会添加到 sys.path）
    """
    from alembic.config import Config

    # 添加模型目录到 sys.path
    if model_path and model_path not in sys.path:
        sys.path.insert(0, model_path)

    script_location = _ensure_alembic_env(model_import_path)

    config = Config()
    config.set_main_option("script_location", script_location)
    config.set_main_option("sqlalchemy.url", _get_db_url())

    return config


def generate_models(output_path: str, verbose: bool = False) -> None:
    """
    从数据库生成 ORM 模型

    Args:
        output_path: 输出文件路径，如 "src/storage/database/shared/model.py"
        verbose: 是否输出详细信息

    Example:
        >>> from coze_coding_dev_sdk.database import generate_models
        >>> generate_models("src/storage/database/shared/model.py")
    """
    db_url = _get_db_url()

    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # 使用 subprocess 调用 sqlacodegen
    import subprocess

    cmd = ["sqlacodegen", db_url, "--outfile", output_path]
    if verbose:
        print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"sqlacodegen failed: {result.stderr}")

    # 在生成的文件头部添加 Base 导入
    with open(output_path, "r") as f:
        content = f.read()

    # 替换默认的 Base 定义为从 SDK 导入
    import re

    # 删除 "class Base(DeclarativeBase):\n    pass\n"
    content = re.sub(r"class Base\(DeclarativeBase\):\s*\n\s*pass\s*\n*", "", content)

    # 删除 DeclarativeBase 相关导入
    content = re.sub(r",\s*DeclarativeBase", "", content)
    content = re.sub(r"DeclarativeBase,\s*", "", content)
    content = re.sub(r"from sqlalchemy\.orm import DeclarativeBase\n", "", content)

    # 在文件开头添加 SDK 的 Base 导入
    content = "from coze_coding_dev_sdk.database import Base\n\n" + content

    with open(output_path, "w") as f:
        f.write(content)

    if verbose:
        print(f"Models generated at {output_path}")


def upgrade(
    model_import_path: str = "storage.database.shared.model",
    model_path: Optional[str] = None,
    verbose: bool = False,
    version_table: str = "schema_version",
    version_table_schema: str = "internal",
) -> None:
    """
    执行数据库迁移（包含自动生成迁移版本）

    相当于执行：
    1. alembic revision --autogenerate
    2. alembic upgrade head

    Args:
        model_import_path: 模型导入路径，如 "storage.database.shared.model"
        model_path: 模型文件所在目录（会添加到 sys.path）
        verbose: 是否输出详细信息
        version_table: 版本表名，默认 "schema_version"
        version_table_schema: 版本表所在 schema，默认 "internal"

    Example:
        >>> from coze_coding_dev_sdk.database import upgrade
        >>> upgrade()  # 使用默认配置
        >>> upgrade(model_import_path="myapp.models", model_path="/path/to/src")
    """
    from alembic import command
    from sqlalchemy import create_engine, text

    # 确保 version_table_schema 存在
    db_url = _get_db_url()
    engine = create_engine(db_url, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{version_table_schema}"'))
    engine.dispose()

    config = _get_alembic_config(model_import_path, model_path)

    # 设置 -x 参数
    config.cmd_opts = type("obj", (object,), {"x": [
        f"version_table={version_table}",
        f"version_table_schema={version_table_schema}",
    ]})()

    # 去除 alembic 输出的前导空格
    config.print_stdout = lambda msg, *args: print(msg.lstrip() % args if args else msg.lstrip())

    # 自动生成迁移版本
    try:
        command.revision(config, message="auto migration", autogenerate=True)
        if verbose:
            print("Migration revision generated")
    except Exception as e:
        # 如果没有变更，revision 可能会失败，忽略
        logger.debug(f"Revision generation skipped: {e}")

    # 执行升级
    command.upgrade(config, "head")
    if verbose:
        print("Database upgraded to head")
    logger.info("Database upgraded to head")


__all__ = [
    "generate_models",
    "upgrade",
]
