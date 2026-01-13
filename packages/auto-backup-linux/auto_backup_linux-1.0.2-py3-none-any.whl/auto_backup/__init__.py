# -*- coding: utf-8 -*-
"""
Auto Backup - 自动备份工具包

一个用于Linux服务器的自动备份工具，支持文件备份、压缩和上传到云端。
"""

__version__ = "1.0.1"
__author__ = "YLX Studio"

from .config import BackupConfig
from .manager import BackupManager
from . import cli

__all__ = ["BackupConfig", "BackupManager", "cli"]

