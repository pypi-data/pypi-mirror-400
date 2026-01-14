"""
r321f 开发者模式入口脚本
"""

import sys
from ..core.developer_mode import DeveloperMode


def main():
    """主函数"""
    dev_mode = DeveloperMode()
    dev_mode.run_interactive_mode()


if __name__ == '__main__':
    main()