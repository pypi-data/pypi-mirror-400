from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_data_dir


APP_NAME = "file-labeler"
APP_AUTHOR = "dreamer"
ENV_DATA_DIR = "FILE_LABELER_DATA_DIR"


def get_data_dir() -> Path:
    """
    返回跨平台用户可写的数据目录。

    优先级：
    1) 环境变量 FILE_LABELER_DATA_DIR
    2) platformdirs.user_data_dir(APP_NAME, APP_AUTHOR)
    """
    override = (os.environ.get(ENV_DATA_DIR) or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(user_data_dir(APP_NAME, APP_AUTHOR)).expanduser().resolve()


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_projects_dir() -> Path:
    return ensure_dir(get_data_dir() / "projects")


def get_image_mirror_dir() -> Path:
    return ensure_dir(get_data_dir() / "image_mirror")


def get_database_path() -> Path:
    ensure_dir(get_data_dir())
    return get_data_dir() / "file_label.db"


def get_whitelist_path() -> Path:
    ensure_dir(get_data_dir())
    return get_data_dir() / "whitelist.json"


