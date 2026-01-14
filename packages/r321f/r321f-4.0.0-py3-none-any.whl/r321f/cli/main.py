"""
r321f 命令行接口
"""

import argparse
import sys
import os
import getpass
from ..core.encryptor import FileEncryptor
from ..core.decryptor import FileDecryptor
from ..core.key_manager import KeyManager
from ..core.encryption_levels import EncryptionLevel, get_encryption_level, get_level_config
from ..core.initializer import R321FInitializer
from ..core.developer_mode import DeveloperMode
from ..utils.platform_utils import get_platform_specific_path


# 颜色支持
COLORS_ENABLED = True

def enable_colors(enabled=True):
    """启用或禁用颜色输出"""
    global COLORS_ENABLED
    COLORS_ENABLED = enabled

def print_colored(text, color=None):
    """打印带颜色的文本"""
    if COLORS_ENABLED and color:
        color_codes = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'reset': '\033[0m'
        }
        print(f"{color_codes.get(color, '')}{text}{color_codes['reset']}")
    else:
        print(text)

def main():
    """主函数"""
    global COLORS_ENABLED

    # 检查是否是特殊命令
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init':
            handle_init()
            return
        elif sys.argv[1] == 'about':
            handle_about()
            return
        elif sys.argv[1] == '--no-color':
            enable_colors(False)
            # 移除 --no-color 参数并继续
            sys.argv.pop(1)
            if len(sys.argv) > 1 and sys.argv[1] == 'about':
                handle_about()
                return

    parser = argparse.ArgumentParser(
        description='r321f - 文件加密解密工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
╔═══════════════════════════════════════════════════════════════════╗
║                        使用示例                                    ║
╚═══════════════════════════════════════════════════════════════════╝

初始化:
  r321f init                          # 初始化 r321f

加密文件:
  r321f encrypt document.pdf -o encrypted.r321f -l P1
  r321f encrypt document.pdf -p mypassword
  r321f encrypt document.pdf --text    # 加密为文本格式

解密文件:
  r321f decrypt encrypted.r321f -o document.pdf
  r321f decrypt encrypted.r321f -p mypassword
  r321f decrypt --text "encrypted_text_here" -o document.pdf

密钥管理:
  r321f encrypt document.pdf -k mykey.key
  r321f decrypt encrypted.r321f -k mykey.key
  r321f key generate mykey             # 生成新密钥
  r321f key list                       # 列出所有密钥

高级功能:
  r321f encrypt document.pdf --dual-auth  # 双重认证
  r321f encrypt document.pdf -d /path/to/output
  r321f np --init                      # 初始化内置密钥
  r321f np --decrypt                   # 解密内置密钥

其他:
  r321f about                          # 查看关于信息
  r321f --no-color encrypt file.txt    # 禁用颜色输出
  r321f-tui                            # 启动 TUI 界面

╔═══════════════════════════════════════════════════════════════════╗
║                        加密级别                                   ║
╚═══════════════════════════════════════════════════════════════════╝

  P-1  - 极低安全级别（仅用于测试）
  P0   - 低安全级别（快速加密）
  P1   - 中等安全级别（推荐）
  P2   - 高安全级别（更安全但较慢）
  P3   - 极高安全级别（最安全但最慢）

更多信息请访问: https://pypi.org/project/r321f/
        """
    )

    parser.add_argument('--no-color', action='store_true', help='禁用颜色输出')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 初始化命令
    init_parser = subparsers.add_parser('init', help='初始化 r321f')
    init_parser.add_argument('--force', action='store_true', help='强制重新初始化')
    init_parser.add_argument('--skip-network-check', action='store_true', help='跳过网络检查')

    # 加密命令
    encrypt_parser = subparsers.add_parser('encrypt', help='加密文件')
    encrypt_parser.add_argument('input', help='输入文件路径')
    encrypt_parser.add_argument('-o', '--output', help='输出文件路径')
    encrypt_parser.add_argument('-d', '--output-dir', help='输出目录')
    encrypt_parser.add_argument('-p', '--password', help='加密密码')
    encrypt_parser.add_argument('-k', '--key-file', help='密钥文件路径')
    encrypt_parser.add_argument('-l', '--level', help='加密级别 (P-2, P-1, P0, P1, P2, P3)', default='P1')
    encrypt_parser.add_argument('--text', action='store_true', help='加密为文本格式（输出到终端）')
    encrypt_parser.add_argument('--dual-auth', action='store_true', help='使用双重认证')
    encrypt_parser.add_argument('--file-type-key', action='store_true', help='使用文件类型特定密钥')

    # 解密命令
    decrypt_parser = subparsers.add_parser('decrypt', help='解密文件')
    decrypt_parser.add_argument('input', nargs='?', help='输入文件路径（或使用--text从文本解密）')
    decrypt_parser.add_argument('-o', '--output', help='输出文件路径')
    decrypt_parser.add_argument('-d', '--output-dir', help='输出目录')
    decrypt_parser.add_argument('-p', '--password', help='解密密码')
    decrypt_parser.add_argument('-k', '--key-file', help='密钥文件路径')
    decrypt_parser.add_argument('--text', help='从文本解密（加密的文本内容）')
    decrypt_parser.add_argument('--dual-auth', action='store_true', help='使用双重认证')

    # 密钥管理命令
    key_parser = subparsers.add_parser('key', help='密钥管理')
    key_subparsers = key_parser.add_subparsers(dest='key_command', help='密钥子命令')

    key_generate = key_subparsers.add_parser('generate', help='生成新密钥')
    key_generate.add_argument('name', help='密钥名称')
    key_generate.add_argument('--metadata', help='元数据（JSON格式）')

    key_list = key_subparsers.add_parser('list', help='列出所有密钥')

    key_delete = key_subparsers.add_parser('delete', help='删除密钥')
    key_delete.add_argument('name', help='密钥名称')

    # 内置密钥功能（r321f-np）
    np_parser = subparsers.add_parser('np', help='内置密钥管理')
    np_parser.add_argument('--init', action='store_true', help='初始化内置密钥')
    np_parser.add_argument('--decrypt', action='store_true', help='解密内置密钥文件')

    # About 命令
    about_parser = subparsers.add_parser('about', help='关于 r321f')

    # Settings 命令
    settings_parser = subparsers.add_parser('settings', help='设置管理')
    settings_subparsers = settings_parser.add_subparsers(dest='settings_command', help='设置子命令')
    
    settings_get = settings_subparsers.add_parser('get', help='获取设置')
    settings_get.add_argument('--key', help='设置键名')
    
    settings_set = settings_subparsers.add_parser('set', help='设置值')
    settings_set.add_argument('--key', required=True, help='设置键名')
    settings_set.add_argument('--value', required=True, help='设置值')
    
    settings_reset = settings_subparsers.add_parser('reset', help='重置为默认设置')

    args = parser.parse_args()

    # 处理 --no-color 选项
    if args.no_color:
        enable_colors(False)

    # 处理命令
    if args.command == 'encrypt':
        handle_encrypt(args)
    elif args.command == 'decrypt':
        handle_decrypt(args)
    elif args.command == 'key':
        handle_key(args)
    elif args.command == 'np':
        handle_np(args)
    elif args.command == 'about':
        handle_about(args)
    elif args.command == 'settings':
        handle_settings(args)
    else:
        parser.print_help()


def handle_init():
    """处理初始化命令"""
    parser = argparse.ArgumentParser(description='初始化 r321f')
    parser.add_argument('--force', action='store_true', help='强制重新初始化')
    parser.add_argument('--skip-network-check', action='store_true', help='跳过网络检查')
    args = parser.parse_args(sys.argv[2:])

    initializer = R321FInitializer()
    initializer.run_init(force=args.force, skip_network_check=args.skip_network_check)


def handle_about(args=None):
    """处理关于命令"""
    print()
    print_colored("╔═══════════════════════════════════════════════════════════════════╗", 'cyan')
    print_colored("║                                                                   ║", 'cyan')
    print_colored("║                     r321f - 文件加密解密工具                        ║", 'cyan')
    print_colored("║                                                                   ║", 'cyan')
    print_colored("╚═══════════════════════════════════════════════════════════════════╝", 'cyan')
    print()
    print_colored("版本: 1.0.0", 'green')
    print_colored("作者: ruin321", 'green')
    print()
    print_colored("开发团队:", 'yellow')
    print_colored("  • Ruin321      - 主程序开发", 'white')
    print_colored("  • schooltaregf - 主程序开发", 'white')
    print_colored("  • flowey       - 灵感来源", 'white')
    print()
    print_colored("特别感谢:", 'yellow')
    print_colored("  • 腾讯 operit QQ群中的群友", 'white')
    print_colored("  • 所有贡献者和支持者", 'white')
    print()
    print_colored("感谢您的使用和支持！", 'cyan')
    print()


def handle_settings(args):
    """处理设置命令"""
    from ..core.developer_mode import DeveloperMode
    dm = DeveloperMode()
    
    if args.settings_command == 'get':
        settings = dm._load_settings()
        if args.key:
            if args.key in settings:
                print(f"{args.key}: {settings[args.key]}")
            else:
                print(f"设置项 '{args.key}' 不存在")
        else:
            print("当前设置:")
            for key, value in settings.items():
                print(f"  {key}: {value}")
    
    elif args.settings_command == 'set':
        dm.settings = dm._load_settings()
        dm.settings[args.key] = args.value
        dm._save_settings()
        print(f"✓ 设置已更新: {args.key} = {args.value}")
    
    elif args.settings_command == 'reset':
        dm.settings = {}
        dm._save_settings()
        print("✓ 设置已重置为默认值")
    
    else:
        print("请使用: r321f settings get/set/reset")


def handle_encrypt(args):
    """处理加密命令"""
    input_path = os.path.expanduser(args.input)

    if not os.path.exists(input_path):
        print(f"错误: 文件不存在: {input_path}")
        sys.exit(1)

    # 获取加密级别
    try:
        encryption_level = get_encryption_level(args.level)
    except ValueError:
        print(f"错误: 无效的加密级别: {args.level}")
        print("支持的级别: P-2, P-1, P0, P1, P2, P3")
        sys.exit(1)

    # 检查是否需要密码
    config = get_level_config(encryption_level)
    requires_password = config.get("requires_password", True)

    # 获取密码
    password = args.password
    if requires_password and not password:
        if args.dual_auth:
            password1 = getpass.getpass("请输入第一个密码: ")
            password2 = getpass.getpass("请输入第二个密码: ")
            password = password1 + '\x00' + password2
        else:
            password = getpass.getpass("请输入加密密码: ")

    # 创建加密器
    if args.key_file:
        encryptor = FileEncryptor(key_file=args.key_file, encryption_level=encryption_level)
    elif args.dual_auth:
        # 使用双重认证
        passwords = password.split('\x00')
        if len(passwords) != 2:
            print("错误: 双重认证需要两个密码")
            sys.exit(1)

        key_manager = KeyManager()
        key = key_manager.generate_dual_auth_key(passwords[0], passwords[1])
        # 创建临时加密器
        encryptor = FileEncryptor(password=password, encryption_level=encryption_level)
        encryptor.fernet = __import__('cryptography.fernet').fernet.Fernet(key)
    elif args.file_type_key:
        # 使用文件类型特定密钥
        file_ext = os.path.splitext(input_path)[1]
        key_manager = KeyManager()
        key = key_manager.generate_file_type_key(password, file_ext)
        encryptor = FileEncryptor(password=password, encryption_level=encryption_level)
        encryptor.fernet = __import__('cryptography.fernet').fernet.Fernet(key)
    else:
        encryptor = FileEncryptor(password=password, encryption_level=encryption_level)

    # 加密文件
    try:
        if args.text:
            # 加密为文本
            encrypted_text = encryptor.encrypt_to_text(input_path)
            print(f"\n=== 加密后的文本 ===\n")
            print(encrypted_text)
            print(f"\n=== 加密完成 ===")
        else:
            # 加密为文件
            output_path = encryptor.encrypt_file(input_path, args.output, args.output_dir)
            print(f"加密成功: {output_path}")
    except Exception as e:
        print(f"加密失败: {str(e)}")
        sys.exit(1)


def handle_decrypt(args):
    """处理解密命令"""
    input_path = os.path.expanduser(args.input)

    # 检查文件是否存在
    if input_path and not os.path.exists(input_path):
        print(f"错误: 文件不存在: {input_path}")
        sys.exit(1)

    # 读取文件头部检查加密级别
    requires_password = True
    if input_path and os.path.exists(input_path):
        try:
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
                # 解析元数据长度
                metadata_length = int.from_bytes(encrypted_data[:4], byteorder='big')
                # 解析元数据
                metadata_json = encrypted_data[4:4+metadata_length]
                metadata = __import__('json').loads(metadata_json.decode('utf-8'))
                # 检查是否需要密码（支持简化的元数据格式）
                encryption_level_str = metadata.get("encryption_level") or metadata.get("l", "P1")
                encryption_level = get_encryption_level(encryption_level_str)
                config = get_level_config(encryption_level)
                requires_password = config.get("requires_password", True)
        except Exception:
            # 如果无法解析元数据，默认需要密码
            requires_password = True

    # 获取密码
    password = args.password
    if requires_password and not password and not args.key_file:
        if args.dual_auth:
            password1 = getpass.getpass("请输入第一个密码: ")
            password2 = getpass.getpass("请输入第二个密码: ")
            password = password1 + '\x00' + password2
        else:
            password = getpass.getpass("请输入解密密码: ")

    # 创建解密器
    if args.key_file:
        decryptor = FileDecryptor(key_file=args.key_file)
    elif args.dual_auth:
        passwords = password.split('\x00')
        if len(passwords) != 2:
            print("错误: 双重认证需要两个密码")
            sys.exit(1)

        key_manager = KeyManager()
        key = key_manager.generate_dual_auth_key(passwords[0], passwords[1])
        decryptor = FileDecryptor(password=password)
        decryptor.fernet = __import__('cryptography.fernet').fernet.Fernet(key)
    else:
        decryptor = FileDecryptor(password=password if requires_password else None)

    # 解密文件
    try:
        if args.text:
            # 从文本解密
            output_path = decryptor.decrypt_from_text(args.text, args.output, args.output_dir)
            print(f"解密成功: {output_path}")
        else:
            input_path = os.path.expanduser(args.input)
            if not input_path:
                print("错误: 请指定输入文件路径")
                sys.exit(1)

            if not os.path.exists(input_path):
                print(f"错误: 文件不存在: {input_path}")
                sys.exit(1)

            output_path = decryptor.decrypt_file(input_path, args.output, args.output_dir)
            print(f"解密成功: {output_path}")
    except Exception as e:
        print(f"解密失败: {str(e)}")
        sys.exit(1)


def handle_key(args):
    """处理密钥管理命令"""
    key_manager = KeyManager()

    if args.key_command == 'generate':
        key = key_manager.generate_key()
        metadata = None
        if args.metadata:
            import json
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print("错误: 元数据格式不正确，应该是JSON格式")
                sys.exit(1)

        key_path = key_manager.save_key(key, args.name, metadata)
        print(f"密钥已生成并保存: {key_path}")

    elif args.key_command == 'list':
        keys = key_manager.list_keys()
        if not keys:
            print("没有找到密钥")
        else:
            print("可用的密钥:")
            for key in keys:
                print(f"  - {key['name']} (创建于: {key['created_at']})")
                if key['metadata']:
                    print(f"    元数据: {key['metadata']}")

    elif args.key_command == 'delete':
        if key_manager.delete_key(args.name):
            print(f"密钥已删除: {args.name}")
        else:
            print(f"密钥不存在: {args.name}")


def handle_np(args):
    """处理内置密钥功能（r321f-np）"""
    key_manager = KeyManager()

    if args.init:
        # 初始化内置密钥
        print("初始化内置密钥...")
        password = getpass.getpass("请输入保护密码: ")
        confirm_password = getpass.getpass("请再次输入密码: ")

        if password != confirm_password:
            print("错误: 密码不匹配")
            sys.exit(1)

        # 生成密钥
        key = key_manager.generate_key()

        # 加密密钥文件
        output_path = get_platform_specific_path('.r321f/encrypted_key.dat')
        key_manager.encrypt_key_file(key, password, output_path)

        print(f"内置密钥已初始化并保存到: {output_path}")

    elif args.decrypt:
        # 解密内置密钥文件
        encrypted_key_path = get_platform_specific_path('.r321f/encrypted_key.dat')

        if not os.path.exists(encrypted_key_path):
            print(f"错误: 内置密钥文件不存在: {encrypted_key_path}")
            print("请先使用 'r321f np --init' 初始化")
            sys.exit(1)

        password = getpass.getpass("请输入保护密码: ")

        try:
            key = key_manager.decrypt_key_file(encrypted_key_path, password)

            # 保存解密后的密钥
            output_path = get_platform_specific_path('.r321f/key.key')
            with open(output_path, 'wb') as f:
                f.write(key)

            print(f"密钥已解密并保存到: {output_path}")
            print("现在可以使用这个密钥文件进行加密解密操作")
        except Exception as e:
            print(f"解密失败: {str(e)}")
            sys.exit(1)
    else:
        print("请指定操作: --init 或 --decrypt")
        print("示例:")
        print("  r321f np --init    # 初始化内置密钥")
        print("  r321f np --decrypt # 解密内置密钥文件")


if __name__ == '__main__':
    main()
