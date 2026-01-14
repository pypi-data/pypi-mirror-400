"""
TUI界面 - r321f-tui 功能
"""

import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.text import Text
from rich.box import SIMPLE
from getpass import getpass
from ..core.encryptor import FileEncryptor
from ..core.decryptor import FileDecryptor
from ..core.key_manager import KeyManager
from ..core.encryption_levels import EncryptionLevel, get_level_config, get_encryption_level


class R321FTUI:
    """r321f TUI 界面"""

    def __init__(self):
        self.console = Console()
        self.current_dir = os.getcwd()

    def run(self):
        """运行 TUI 界面"""
        self.console.clear()

        # 显示欢迎界面
        self._show_welcome()

        # 主循环
        while True:
            self._show_main_menu()

            choice = Prompt.ask(
                "\n请选择操作",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "0"],
                default="0"
            )

            if choice == "1":
                self._encrypt_file()
            elif choice == "2":
                self._decrypt_file()
            elif choice == "3":
                self._manage_keys()
            elif choice == "4":
                self._show_info()
            elif choice == "5":
                self._change_directory()
            elif choice == "6":
                self._show_encryption_levels()
            elif choice == "7":
                self._show_settings()
            elif choice == "8":
                self._show_about()
            elif choice == "0":
                self.console.print("\n感谢使用 r321f！", style="bold green")
                break

    def _show_welcome(self):
        """显示欢迎界面"""
        welcome_text = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ████████╗██╗   ██╗██╗ ██████╗ ███╗   ██╗██████╗ ███████╗██████╗ ║
║   ╚══██╔══╝██║   ██║██║██╔════╝ ████╗  ██║██╔══██╗██╔════╝██╔══██╗║
║      ██║   ██║   ██║██║██║  ███╗██╔██╗ ██║██║  ██║█████╗  ██████╔╝║
║      ██║   ╚██╗ ██╔╝██║██║   ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗║
║      ██║    ╚████╔╝ ██║╚██████╔╝██║ ╚████║██████╔╝███████╗██║  ██║║
║      ╚═╝     ╚═══╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝║
║                                                                   ║
║                 文件加密解密工具 - TUI 界面 v1.0.0                 ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
        """

        self.console.print(welcome_text, style="bold cyan")
        self.console.print("\n版本: 1.0.0 | 作者: ruin321", style="dim")
        self.console.print("安全、快速、易用的文件加密解决方案\n", style="green")

    def _show_main_menu(self):
        """显示主菜单"""
        menu = Table(show_header=False, box=None, padding=(0, 2))
        menu.add_column("", style="cyan", width=4)
        menu.add_column("", style="white")
        menu.add_column("", style="dim")

        menu.add_row("【1】", "加密文件", "保护您的文件")
        menu.add_row("【2】", "解密文件", "恢复您的文件")
        menu.add_row("【3】", "密钥管理", "管理加密密钥")
        menu.add_row("【4】", "系统信息", "查看系统详情")
        menu.add_row("【5】", "切换目录", "选择工作目录")
        menu.add_row("【6】", "加密级别", "查看安全级别")
        menu.add_row("【7】", "设置", "配置保存目录等")
        menu.add_row("【8】", "关于", "开发团队信息")
        menu.add_row("【0】", "退出程序", "感谢使用")

        panel = Panel(menu, title="主菜单", border_style="cyan", padding=(1, 1))
        self.console.print(panel)

        # 显示当前目录
        self.console.print(f"\n当前目录: {self.current_dir}", style="dim")

    def _encrypt_file(self):
        """加密文件"""
        self.console.print("\n" + "="*60, style="cyan")
        self.console.print("加密文件", style="bold cyan")
        self.console.print("="*60 + "\n")

        # 选择文件
        file_path = Prompt.ask("请输入要加密的文件路径")
        # 展开路径（支持 ~ 和 $HOME）
        file_path = os.path.expanduser(file_path)
        if not os.path.exists(file_path):
            self.console.print(f"错误: 文件不存在: {file_path}", style="red")
            return

        # 选择加密级别
        self.console.print("\n加密级别:", style="yellow")
        levels = ["P-2", "P-1", "P0", "P1", "P2", "P3"]
        for i, level in enumerate(levels, 1):
            config = get_level_config(get_encryption_level(level))
            self.console.print(f"  [{i}] {config['name']}", style="cyan")
            self.console.print(f"      {config['description']}", style="dim")

        level_choice = Prompt.ask(
            "\n请选择加密级别",
            choices=["1", "2", "3", "4", "5", "6"],
            default="3"
        )
        encryption_level = get_encryption_level(levels[int(level_choice) - 1])

        # 检查是否需要密码
        config = get_level_config(encryption_level)
        requires_password = config.get("requires_password", True)

        password = None
        if requires_password:
            # 输入密码
            password = getpass("请输入加密密码: ")
            if not password:
                self.console.print("错误: 密码不能为空", style="red")
                return

            # 确认密码
            confirm_password = getpass("请再次输入密码: ")
            if password != confirm_password:
                self.console.print("错误: 两次输入的密码不一致", style="red")
                return

        # 加密文件
        try:
            self.console.print("\n正在加密...", style="yellow")
            encryptor = FileEncryptor(password=password, encryption_level=encryption_level)
            output_path = encryptor.encrypt_file(file_path)
            self.console.print(f"\n✓ 加密成功!", style="bold green")
            self.console.print(f"输出文件: {output_path}", style="cyan")
        except Exception as e:
            self.console.print(f"\n✗ 加密失败: {str(e)}", style="red")

        input("\n按 Enter 继续...")

    def _decrypt_file(self):
        """解密文件"""
        self.console.print("\n" + "="*60, style="cyan")
        self.console.print("解密文件", style="bold cyan")
        self.console.print("="*60 + "\n")

        # 选择文件
        file_path = Prompt.ask("请输入要解密的文件路径")
        # 展开路径（支持 ~ 和 $HOME）
        file_path = os.path.expanduser(file_path)
        if not os.path.exists(file_path):
            self.console.print(f"错误: 文件不存在: {file_path}", style="red")
            return

        # 检查文件是否需要密码
        requires_password = True
        try:
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
                # 解析元数据长度
                metadata_length = int.from_bytes(encrypted_data[:4], byteorder='big')
                # 解析元数据
                metadata_json = encrypted_data[4:4+metadata_length]
                metadata = json.loads(metadata_json.decode('utf-8'))
                # 检查是否需要密码（支持简化的元数据格式）
                encryption_level_str = metadata.get("encryption_level") or metadata.get("l", "P1")
                encryption_level = get_encryption_level(encryption_level_str)
                config = get_level_config(encryption_level)
                requires_password = config.get("requires_password", True)
        except Exception:
            # 如果无法解析元数据，默认需要密码
            requires_password = True

        password = None
        if requires_password:
            # 输入密码
            password = getpass("请输入解密密码: ")
            if not password:
                self.console.print("错误: 密码不能为空", style="red")
                return

        # 解密文件
        try:
            self.console.print("\n正在解密...", style="yellow")
            decryptor = FileDecryptor(password=password)
            output_path = decryptor.decrypt_file(file_path)
            self.console.print(f"\n✓ 解密成功!", style="bold green")
            self.console.print(f"输出文件: {output_path}", style="cyan")
            self.console.print(f"\n文件信息:", style="yellow")
            if decryptor.metadata:
                for key, value in decryptor.metadata.items():
                    self.console.print(f"  {key}: {value}", style="dim")
        except Exception as e:
            self.console.print(f"\n✗ 解密失败: {str(e)}", style="red")

        input("\n按 Enter 继续...")

    def _manage_keys(self):
        """密钥管理"""
        self.console.print("\n" + "="*60, style="cyan")
        self.console.print("密钥管理", style="bold cyan")
        self.console.print("="*60 + "\n")

        key_manager = KeyManager()

        while True:
            self.console.print("密钥管理选项:", style="yellow")
            self.console.print("  [1] 列出所有密钥")
            self.console.print("  [2] 生成新密钥")
            self.console.print("  [3] 删除密钥")
            self.console.print("  [0] 返回主菜单")

            choice = Prompt.ask(
                "\n请选择操作",
                choices=["1", "2", "3", "0"],
                default="0"
            )

            if choice == "1":
                self._list_keys(key_manager)
            elif choice == "2":
                self._generate_key(key_manager)
            elif choice == "3":
                self._delete_key(key_manager)
            elif choice == "0":
                break

    def _list_keys(self, key_manager):
        """列出所有密钥"""
        keys = key_manager.list_keys()

        if not keys:
            self.console.print("\n没有找到密钥", style="yellow")
        else:
            table = Table(title="密钥列表")
            table.add_column("名称", style="cyan")
            table.add_column("创建时间", style="green")
            table.add_column("元数据", style="dim")

            for key in keys:
                metadata_str = str(key['metadata']) if key['metadata'] else "无"
                table.add_row(key['name'], key['created_at'][:10] if key['created_at'] else "未知", metadata_str)

            self.console.print("\n")
            self.console.print(table)

        input("\n按 Enter 继续...")

    def _generate_key(self, key_manager):
        """生成新密钥"""
        key_name = Prompt.ask("\n请输入密钥名称")
        if not key_name:
            self.console.print("错误: 密钥名称不能为空", style="red")
            return

        try:
            key = key_manager.generate_key()
            key_path = key_manager.save_key(key, key_name)
            self.console.print(f"\n✓ 密钥已生成: {key_path}", style="green")
        except Exception as e:
            self.console.print(f"\n✗ 生成密钥失败: {str(e)}", style="red")

        input("\n按 Enter 继续...")

    def _delete_key(self, key_manager):
        """删除密钥"""
        key_name = Prompt.ask("\n请输入要删除的密钥名称")
        if not key_name:
            self.console.print("错误: 密钥名称不能为空", style="red")
            return

        if Confirm.ask(f"确定要删除密钥 '{key_name}' 吗？"):
            if key_manager.delete_key(key_name):
                self.console.print(f"\n✓ 密钥已删除", style="green")
            else:
                self.console.print(f"\n✗ 密钥不存在", style="red")

        input("\n按 Enter 继续...")

    def _show_info(self):
        """显示系统信息"""
        self.console.print("\n" + "="*60, style="cyan")
        self.console.print("系统信息", style="bold cyan")
        self.console.print("="*60 + "\n")

        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column("项目", style="cyan")
        info_table.add_column("值", style="white")

        import platform
        info_table.add_row("版本", "2.0.0")
        info_table.add_row("作者", "ruin321")
        info_table.add_row("系统", platform.system())
        info_table.add_row("Python版本", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        info_table.add_row("工作目录", self.current_dir)

        self.console.print(info_table)

        input("\n按 Enter 继续...")

    def _change_directory(self):
        """切换目录"""
        new_dir = Prompt.ask("\n请输入新的目录路径", default=self.current_dir)
        if os.path.isdir(new_dir):
            self.current_dir = new_dir
            os.chdir(new_dir)
            self.console.print(f"\n✓ 已切换到: {new_dir}", style="green")
        else:
            self.console.print(f"\n✗ 目录不存在: {new_dir}", style="red")

        input("\n按 Enter 继续...")

    def _show_encryption_levels(self):
        """显示加密级别说明"""
        self.console.print("\n" + "="*60, style="cyan")
        self.console.print("加密级别说明", style="bold cyan")
        self.console.print("="*60 + "\n")

        levels = [EncryptionLevel.P_NEGATIVE_2, EncryptionLevel.P_NEGATIVE_1, EncryptionLevel.P0, EncryptionLevel.P1, EncryptionLevel.P2, EncryptionLevel.P3]

        for level in levels:
            config = get_level_config(level)
            self.console.print(f"\n{config['name']}", style="bold cyan")
            self.console.print(f"  描述: {config['description']}", style="white")
            self.console.print(f"  迭代次数: {config['iterations']}", style="dim")
            self.console.print(f"  使用盐值: {'是' if config['use_salt'] else '否'}", style="dim")

        input("\n按 Enter 继续...")

    def _show_about(self):
        """显示关于信息"""
        self.console.print("\n" + "="*60, style="cyan")
        self.console.print("关于 r321f", style="bold cyan")
        self.console.print("="*60 + "\n")

        about_table = Table(show_header=False, box=None, padding=(0, 2))
        about_table.add_column("", style="cyan")
        about_table.add_column("", style="white")

        about_table.add_row("版本", "1.0.0")
        about_table.add_row("作者", "ruin321")
        about_table.add_row("", "")
        about_table.add_row("开发团队:", "")
        about_table.add_row("  • Ruin321", "主程序开发")
        about_table.add_row("  • schooltaregf", "主程序开发")
        about_table.add_row("  • flowey", "灵感来源")
        about_table.add_row("", "")
        about_table.add_row("特别感谢:", "")
        about_table.add_row("  • 腾讯 operit QQ群中的群友", "")
        about_table.add_row("  • 所有贡献者和支持者", "")

        self.console.print(about_table)
        self.console.print("\n感谢您的使用和支持！", style="green")

        input("\n按 Enter 继续...")

    def _show_settings(self):
        """显示设置信息"""
        from ..core.developer_mode import DeveloperMode
        dm = DeveloperMode()
        settings = dm._load_settings()

        self.console.print("\n" + "="*60, style="cyan")
        self.console.print("设置管理", style="bold cyan")
        self.console.print("="*60 + "\n")

        settings_table = Table(show_header=True, box=SIMPLE, padding=(0, 2))
        settings_table.add_column("设置项", style="cyan")
        settings_table.add_column("当前值", style="white")
        settings_table.add_column("说明", style="dim")

        settings_table.add_row("save_directory", settings.get('save_directory', '未设置'), '文件保存目录')
        settings_table.add_row("", "", "")
        settings_table.add_row("[yellow]提示[/yellow]", "", "")
        settings_table.add_row("", "", "使用 'r321f settings set --key save_directory --value /path/to/dir' 修改")
        settings_table.add_row("", "", "使用 'r321f settings reset' 重置为默认")

        self.console.print(settings_table)
        input("\n按 Enter 继续...")


def main():
    """主函数"""
    try:
        tui = R321FTUI()
        tui.run()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()