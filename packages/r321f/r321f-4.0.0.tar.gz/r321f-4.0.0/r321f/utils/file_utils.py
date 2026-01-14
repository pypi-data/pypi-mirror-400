"""
文件工具函数
"""

import os


def get_file_type(filepath):
    """
    获取文件类型
    
    Args:
        filepath: 文件路径
    
    Returns:
        文件扩展名（小写，包含点号）
    """
    _, ext = os.path.splitext(filepath)
    return ext.lower()


def get_output_path(input_path, output_path=None, output_dir=None, suffix='.r321f'):
    """
    获取输出文件路径
    
    Args:
        input_path: 输入文件路径
        output_path: 指定的输出路径（可选）
        output_dir: 输出目录（可选）
        suffix: 文件后缀（默认为.r321f）
    
    Returns:
        输出文件路径
    """
    if output_path:
        return output_path
    
    if output_dir:
        filename = os.path.basename(input_path)
        if not filename.endswith(suffix):
            filename = filename + suffix
        return os.path.join(output_dir, filename)
    
    # 默认：在原文件名后添加后缀
    return input_path + suffix


def is_encrypted_file(filepath):
    """
    检查是否是加密文件
    
    Args:
        filepath: 文件路径
    
    Returns:
        如果是加密文件返回True，否则返回False
    """
    return filepath.endswith('.r321f')