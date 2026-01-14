"""
工具模块
"""

from .file_utils import get_file_type, get_output_path
from .platform_utils import get_platform_specific_path

__all__ = ['get_file_type', 'get_output_path', 'get_platform_specific_path']