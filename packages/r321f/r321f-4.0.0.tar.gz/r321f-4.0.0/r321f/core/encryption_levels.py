"""
加密级别定义
"""

from enum import Enum
from typing import Dict, Any


class EncryptionLevel(Enum):
    """加密级别枚举"""
    P_NEGATIVE_2 = "P-2"  # 纯文本编码，无密码，仅 base64 编码
    P_NEGATIVE_1 = "P-1"  # 仅文本加密，无盐值，可随意传播
    P0 = "P0"              # 简单加密，使用固定盐值
    P1 = "P1"              # 标准加密，使用随机盐值
    P2 = "P2"              # 高级加密，使用随机盐值 + 双重认证
    P3 = "P3"              # 最高级加密，使用随机盐值 + 双重认证 + 文件类型密钥


# 加密级别配置
ENCRYPTION_LEVEL_CONFIG = {
    EncryptionLevel.P_NEGATIVE_2: {
        "name": "P-2 - 纯文本编码",
        "description": "无密码加密，仅使用 base64 编码，适合公开分享",
        "use_salt": False,
        "iterations": 0,
        "requires_password": False,
        "supports_file_type_key": False,
        "supports_dual_auth": False,
    },
    EncryptionLevel.P_NEGATIVE_1: {
        "name": "P-1 - 纯文本加密",
        "description": "仅加密为文本格式，无盐值保护，可随意传播",
        "use_salt": False,
        "iterations": 10000,
        "requires_password": True,
        "supports_file_type_key": False,
        "supports_dual_auth": False,
    },
    EncryptionLevel.P0: {
        "name": "P0 - 基础加密",
        "description": "简单加密，使用固定盐值，适合临时加密",
        "use_salt": False,
        "fixed_salt": b'r321f_p0_salt',
        "iterations": 50000,
        "requires_password": True,
        "supports_file_type_key": False,
        "supports_dual_auth": False,
    },
    EncryptionLevel.P1: {
        "name": "P1 - 标准加密",
        "description": "标准加密，使用随机盐值，适合日常使用",
        "use_salt": True,
        "iterations": 100000,
        "requires_password": True,
        "supports_file_type_key": False,
        "supports_dual_auth": False,
    },
    EncryptionLevel.P2: {
        "name": "P2 - 高级加密",
        "description": "高级加密，使用随机盐值和双重认证，适合敏感文件",
        "use_salt": True,
        "iterations": 200000,
        "requires_password": True,
        "supports_file_type_key": False,
        "supports_dual_auth": True,
    },
    EncryptionLevel.P3: {
        "name": "P3 - 最高级加密",
        "description": "最高级加密，使用随机盐值、双重认证和文件类型密钥，适合绝密文件",
        "use_salt": True,
        "iterations": 300000,
        "requires_password": True,
        "supports_file_type_key": True,
        "supports_dual_auth": True,
    },
}


def get_encryption_level(level_str: str) -> EncryptionLevel:
    """
    根据字符串获取加密级别

    Args:
        level_str: 加密级别字符串 (P-2, P-1, P0, P1, P2, P3)

    Returns:
        EncryptionLevel 枚举值
    """
    level_map = {
        "P-2": EncryptionLevel.P_NEGATIVE_2,
        "P-1": EncryptionLevel.P_NEGATIVE_1,
        "P0": EncryptionLevel.P0,
        "P1": EncryptionLevel.P1,
        "P2": EncryptionLevel.P2,
        "P3": EncryptionLevel.P3,
    }
    return level_map.get(level_str.upper(), EncryptionLevel.P1)


def get_level_config(level: EncryptionLevel) -> Dict[str, Any]:
    """
    获取加密级别配置

    Args:
        level: 加密级别枚举

    Returns:
        配置字典
    """
    return ENCRYPTION_LEVEL_CONFIG.get(level, ENCRYPTION_LEVEL_CONFIG[EncryptionLevel.P1])