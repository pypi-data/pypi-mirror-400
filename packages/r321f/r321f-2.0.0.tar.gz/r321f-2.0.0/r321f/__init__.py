"""
r321f - 文件加密解密工具包
支持多种文件格式的加密解密，包括压缩包、文档、Office文档、可执行程序等
"""

__version__ = "2.0.0"
__author__ = "ruin321"

from .core.encryptor import FileEncryptor
from .core.decryptor import FileDecryptor
from .core.key_manager import KeyManager
from .core.encryption_levels import EncryptionLevel, get_encryption_level, get_level_config
from .core.initializer import R321FInitializer
from .core.developer_mode import DeveloperMode

__all__ = [
    'FileEncryptor',
    'FileDecryptor',
    'KeyManager',
    'EncryptionLevel',
    'get_encryption_level',
    'get_level_config',
    'R321FInitializer',
    'DeveloperMode'
]