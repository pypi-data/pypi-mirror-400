from __future__ import annotations

import argparse
import os
from typing import Optional

from .paths import ENV_DATA_DIR

ENV_PASSWORD = "FILE_LABELER_PASSWORD"
ENV_SECRET_KEY = "FILE_LABELER_SECRET_KEY"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="file-labeler", description="file-labeler Web 服务启动器")
    p.add_argument("--host", default="0.0.0.0", help="监听地址，默认 0.0.0.0")
    p.add_argument("--port", type=int, default=17007, help="监听端口，默认 17007")
    p.add_argument("--debug", action="store_true", help="开启 Flask debug（不建议生产使用）")
    p.add_argument(
        "--data-dir",
        default=None,
        help=f"数据目录（覆盖环境变量 {ENV_DATA_DIR}），用于保存数据库/白名单/镜像等",
    )
    p.add_argument(
        "--password",
        default=None,
        help=f"登录密码（覆盖环境变量 {ENV_PASSWORD}）；未设置时将使用默认值（不建议生产环境）",
    )
    p.add_argument(
        "--secret-key",
        default=None,
        help=f"Flask SECRET_KEY（覆盖环境变量 {ENV_SECRET_KEY}）；未设置时将自动生成随机值（重启后 session 失效）",
    )
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.data_dir:
        os.environ[ENV_DATA_DIR] = args.data_dir
    if args.password:
        os.environ[ENV_PASSWORD] = args.password
    if args.secret_key:
        os.environ[ENV_SECRET_KEY] = args.secret_key

    # 延迟导入，确保 data-dir 环境变量生效后再初始化 config/database
    from .webapp import app  # noqa: WPS433

    app.run(debug=bool(args.debug), host=args.host, port=int(args.port))
    return 0


