"""
数据库 CLI 命令
"""

import os
import click

# 默认路径
DEFAULT_MODEL_OUTPUT = "src/storage/database/shared/model.py"
DEFAULT_MODEL_IMPORT_PATH = "storage.database.shared.model"
DEFAULT_MODEL_PATH = "src"


def _get_workspace_path() -> str:
    """获取工作目录"""
    return os.getenv("WORKSPACE_PATH", os.getcwd())


@click.group()
def db():
    """Database management commands."""
    pass


@db.command()
@click.argument("output_path", required=False, default=None)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def generate_models(output_path: str, verbose: bool):
    """
    Generate ORM models from database.

    OUTPUT_PATH: Path to output model file (default: src/storage/database/shared/model.py)
    """
    from coze_coding_dev_sdk.database import generate_models as _generate_models

    if output_path is None:
        workspace = _get_workspace_path()
        output_path = os.path.join(workspace, DEFAULT_MODEL_OUTPUT)

    try:
        _generate_models(output_path, verbose=verbose)
        click.echo(f"Models generated at {output_path}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@db.command()
@click.option(
    "--model-import-path",
    default=DEFAULT_MODEL_IMPORT_PATH,
    help=f"Model import path (default: {DEFAULT_MODEL_IMPORT_PATH})",
)
@click.option(
    "--model-path",
    default=None,
    help=f"Path to add to sys.path for model import (default: $WORKSPACE_PATH/{DEFAULT_MODEL_PATH})",
)
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def upgrade(model_import_path: str, model_path: str, verbose: bool):
    """
    Run database migrations.

    Automatically generates migration and upgrades to head.
    """
    from coze_coding_dev_sdk.database import upgrade as _upgrade

    if model_path is None:
        workspace = _get_workspace_path()
        model_path = os.path.join(workspace, DEFAULT_MODEL_PATH)

    try:
        _upgrade(
            model_import_path=model_import_path,
            model_path=model_path,
            verbose=verbose,
        )
        click.echo("Database upgraded successfully")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
