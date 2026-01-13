# file-labeler

一个基于 Flask 的文件分类标注 Web 工具

## 安装

```bash
pip install file-labeler
```

## 启动

```bash
file-labeler --host 0.0.0.0 --port 17007
```

## 安全配置（强烈建议）

默认会使用内置的登录密码（仅用于本地/内网快速使用），发布/生产环境请务必设置环境变量或通过命令行覆盖：

```bash
# Linux/macOS
export FILE_LABELER_PASSWORD="your-strong-password"
export FILE_LABELER_SECRET_KEY="your-secret-key"
```

```bash
# Windows PowerShell
setx FILE_LABELER_PASSWORD "your-strong-password"
setx FILE_LABELER_SECRET_KEY "your-secret-key"
```

或命令行参数：

```bash
file-labeler --password "your-strong-password" --secret-key "your-secret-key"
```

## Windows 兼容说明（数据目录）

运行时产生的数据（SQLite 数据库、白名单、镜像目录等）会写入用户可写目录（通过 `platformdirs` 自动选择，Windows 下为用户的 AppData 目录）。

你也可以用环境变量覆盖：

```bash
set FILE_LABELER_DATA_DIR=D:\file_labeler_data
```

或命令行参数：

```bash
file-labeler --data-dir D:\file_labeler_data
```


