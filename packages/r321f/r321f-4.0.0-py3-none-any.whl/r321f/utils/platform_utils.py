"""
平台相关工具函数
"""

import os
import platform


def get_platform_specific_path(subpath):
    """
    获取平台特定的路径
    
    Args:
        subpath: 子路径
    
    Returns:
        平台特定的完整路径
    """
    system = platform.system()
    
    if system == 'Windows':
        # Windows: C盘根目录或用户目录
        if os.path.exists('C:\\'):
            base_path = 'C:\\'
        else:
            base_path = os.path.expanduser('~')
    elif system == 'Darwin':
        # macOS: 用户目录
        base_path = os.path.expanduser('~')
    else:
        # Linux/Unix: 用户目录
        base_path = os.path.expanduser('~')
    
    return os.path.join(base_path, subpath)


def get_platform():
    """
    获取当前平台
    
    Returns:
        平台名称（Windows, Darwin, Linux）
    """
    return platform.system()


def is_windows():
    """检查是否是Windows系统"""
    return platform.system() == 'Windows'


def is_macos():
    """检查是否是macOS系统"""
    return platform.system() == 'Darwin'


def is_linux():
    """检查是否是Linux系统"""
    return platform.system() == 'Linux'