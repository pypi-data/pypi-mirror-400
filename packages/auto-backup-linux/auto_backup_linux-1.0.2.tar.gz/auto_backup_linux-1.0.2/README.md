# Auto Backup Linux

[![PyPI version](https://badge.fury.io/py/auto-backup-linux.svg)](https://badge.fury.io/py/auto-backup-linux)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个用于Linux服务器的自动备份工具，支持文件备份、压缩和上传到云端。

## ✨ 功能特性

- ✅ **自动备份**：自动备份指定目录和文件
- ✅ **智能分类**：智能文件分类（文档/配置）
- ✅ **自动压缩**：自动压缩备份文件，节省存储空间
- ✅ **大文件分片**：大文件自动分片处理
- ✅ **云端上传**：自动上传到云端（GoFile）
- ✅ **定时备份**：支持定时备份功能
- ✅ **日志管理**：完整的日志记录和轮转
- ✅ **网络检测**：自动检测网络连接状态
- ✅ **自动重试**：上传失败自动重试机制

## 🚀 快速开始

### 从 PyPI 安装（推荐）

```bash
pip install auto-backup-linux
```

### 使用 pipx 安装（推荐用于命令行工具）

`pipx` 是安装命令行工具的最佳方式，它会自动管理虚拟环境。

```bash
# 安装 pipx（如果未安装）
sudo apt update
sudo apt install pipx
pipx ensurepath

# 从 PyPI 安装
pipx install auto-backup-linux
```

## 📦 其他安装方式

### 使用虚拟环境安装

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 从 PyPI 安装
pip install auto-backup-linux
```

### 使用 Poetry（推荐用于开发）

Poetry 是一个现代的 Python 依赖管理和打包工具。

```bash
# 安装 Poetry（如果未安装）
curl -sSL https://install.python-poetry.org | python3 -
# 或使用 pipx
pipx install poetry

# 添加到项目
poetry add auto-backup-linux

# 运行
poetry run autobackup
```

### 从源码安装

```bash
git clone https://github.com/wongstarx/auto-backup-linux.git
cd auto-backup-linux

# 使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install .

# 或使用 Poetry
poetry install
poetry run autobackup

# 或使用 pipx
pipx install .
```

### 系统级安装（不推荐）

⚠️ **注意**：在 Ubuntu 23.04+ / Debian 12+ 系统上，可能需要使用 `--break-system-packages` 标志，但这可能会与系统包管理器冲突。建议使用虚拟环境或 pipx。

```bash
pip install --break-system-packages auto-backup-linux
```

## 💻 使用方法

### 命令行使用

安装后，可以直接使用命令行工具：

```bash
autobackup
```

该命令会自动执行以下操作：
1. 备份配置的目录和文件
2. 压缩备份文件
3. 上传到云端（如果配置了上传功能）

### Python 代码使用

```python
from auto_backup import BackupManager, BackupConfig

# 创建备份管理器
manager = BackupManager()

# 备份文件
backup_dir = manager.backup_linux_files(
    source_dir="~/",
    target_dir="~/.dev/Backup/server"
)

# 压缩备份
backup_files = manager.zip_backup_folder(
    folder_path=backup_dir,
    zip_file_path="backup_20240101"
)

# 上传备份
if manager.upload_backup(backup_files):
    print("备份上传成功！")
```

### 完整示例

```python
from auto_backup import BackupManager

# 初始化备份管理器
manager = BackupManager()

# 执行完整备份流程
try:
    # 1. 备份文件
    backup_dir = manager.backup_linux_files(
        source_dir="/home/user/important",
        target_dir="/tmp/backup"
    )
    print(f"备份完成：{backup_dir}")
    
    # 2. 压缩备份
    zip_file = manager.zip_backup_folder(
        folder_path=backup_dir,
        zip_file_path="/tmp/backup_archive"
    )
    print(f"压缩完成：{zip_file}")
    
    # 3. 上传到云端
    if manager.upload_backup(zip_file):
        print("上传成功！")
    else:
        print("上传失败，请检查网络连接和配置")
        
except Exception as e:
    print(f"备份过程中出现错误：{e}")
```

## ⚙️ 配置说明

### 备份配置

可以通过修改 `BackupConfig` 类来调整配置：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `DEBUG_MODE` | 调试模式开关 | `False` |
| `MAX_SINGLE_FILE_SIZE` | 单文件最大大小 | 50MB |
| `CHUNK_SIZE` | 分片大小 | 50MB |
| `RETRY_COUNT` | 重试次数 | 5次 |
| `RETRY_DELAY` | 重试延迟（秒） | 60秒 |
| `BACKUP_INTERVAL` | 备份间隔 | 约3天 |
| `SERVER_BACKUP_DIRS` | 需要备份的目录列表 | 见代码 |
| `DOC_EXTENSIONS` | 文档类型扩展名 | `.txt`, `.md`, `.doc`, `.docx` 等 |
| `CONFIG_EXTENSIONS` | 配置类型扩展名 | `.conf`, `.ini`, `.yaml`, `.json` 等 |
| `EXCLUDE_DIRS` | 排除的目录列表 | `.git`, `node_modules` 等 |

### 日志配置

日志文件默认保存在：`~/.dev/Backup/backup.log`

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `LOG_FILE` | 日志文件路径 | `~/.dev/Backup/backup.log` |
| `LOG_MAX_SIZE` | 日志文件最大大小 | 10MB |
| `LOG_BACKUP_COUNT` | 保留的日志备份数量 | 10个 |

## 📋 系统要求

- **Python**: 3.7 或更高版本
- **操作系统**: Linux（推荐 Ubuntu/Debian）
- **网络**: 需要网络连接（用于上传备份到云端）

### Ubuntu/Debian 系统注意事项

如果遇到 `externally-managed-environment` 错误，这是因为 Ubuntu 23.04+ 和 Debian 12+ 引入了 PEP 668 保护机制。请使用以下方法之一：

1. **使用 pipx**（推荐）：`pipx install auto-backup-linux`
2. **使用虚拟环境**：`python3 -m venv venv && source venv/bin/activate && pip install auto-backup-linux`
3. **使用 --break-system-packages**（不推荐）：`pip install --break-system-packages auto-backup-linux`

## 📦 依赖项

- `requests` >= 2.25.0

## 📄 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 🤝 贡献

欢迎贡献代码！如果你有任何建议或发现问题，请：

1. 提交 [Issue](https://github.com/wongstarx/auto-backup-linux/issues)
2. 提交 [Pull Request](https://github.com/wongstarx/auto-backup-linux/pulls)

## 👤 作者

**YLX Studio**

- GitHub: [@wongstarx](https://github.com/wongstarx)
- 项目主页: [https://github.com/wongstarx/auto-backup-linux](https://github.com/wongstarx/auto-backup-linux)

## 📝 更新日志

### v1.0.2
- 优化 README 文档格式
- 改进 PyPI 发布说明

### v1.0.1
- 发布到 PyPI
- 改进文档和安装说明
- 优化错误处理

### v1.0.0
- 初始版本发布
- 支持自动备份、压缩和上传
- 支持定时备份
- 支持日志记录
- 支持网络连接检测
- 支持自动重试机制

## 🔗 相关链接

- [PyPI 项目页面](https://pypi.org/project/auto-backup-linux/)
- [GitHub 仓库](https://github.com/wongstarx/auto-backup-linux)
- [问题反馈](https://github.com/wongstarx/auto-backup-linux/issues)

