import sys
from pathlib import Path
from typing import Union

from alembic import command
from alembic.config import Config

PROJECT_ROOT_DIR = Path(__file__).parent.parent.parent


def get_runtime_root_dir():
    """
    获取项目根目录。
    1. 如果是打包后的应用（如使用 PyInstaller），则返回 _MEIPASS 目录。
    2. 否则，返回本项目的根目录
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return PROJECT_ROOT_DIR


RUNTIME_ROOT_DIR = get_runtime_root_dir()
DATA_DIR = RUNTIME_ROOT_DIR / "data"

for d in [DATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

APP_NAME = "ipa-fms"

DB_URL = f"sqlite:///{DATA_DIR / f'{APP_NAME}.db'}"


def setup_alembic(config: Union[Config, None] = None):
    """
    使用动态数据库URL
    """
    cfg = config or Config(RUNTIME_ROOT_DIR / "alembic.ini")
    if not cfg.get_main_option("sqlalchemy.url"):
        cfg.set_main_option("sqlalchemy.url", DB_URL)
    return cfg


def setup_database():
    """
    初始化数据库，运行数据库迁移脚本
    """

    cfg = setup_alembic()
    command.upgrade(cfg, "head")
