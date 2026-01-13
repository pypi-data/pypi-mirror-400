from __future__ import annotations

from .paths import get_database_path, get_image_mirror_dir, get_projects_dir

# 项目数据目录（保留用于JSON文件迁移）
PROJECTS_DIR = str(get_projects_dir())

# SQLite数据库路径
DATABASE_PATH = str(get_database_path())

# 图片镜像目录
IMAGE_MIRROR_DIR = str(get_image_mirror_dir())

# 支持的图片格式
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif"}


