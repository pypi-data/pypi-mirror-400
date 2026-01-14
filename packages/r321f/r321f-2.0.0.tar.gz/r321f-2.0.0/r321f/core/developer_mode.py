"""
开发者模式 - r321f-CRonly 功能
"""

import os
import sys
import json
import getpass
import tkinter as tk
from tkinter import simpledialog, messagebox
from typing import List, Dict, Optional
from datetime import datetime


class DeveloperMode:
    """开发者模式管理器"""

    # 开发者密码
    DEVELOPER_PASSWORDS = [
        "r321f_is_forver",
        "r321f"
    ]

    def __init__(self, config_dir=None):
        """
        初始化开发者模式

        Args:
            config_dir: 配置目录
        """
        if config_dir is None:
            home_dir = os.path.expanduser('~')
            self.config_dir = os.path.join(home_dir, '.r321f')
        else:
            self.config_dir = config_dir

        self.developer_files_path = os.path.join(self.config_dir, 'developer_files.json')
        self.settings_path = os.path.join(self.config_dir, 'settings.json')
        self.authenticated = False
        self.settings = self._load_settings()

    def _load_settings(self):
        """加载设置"""
        default_settings = {
            'save_directory': self._get_default_save_directory(),
            'auto_save_to_config_dir': False
        }

        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                default_settings.update(settings)
            except:
                pass

        return default_settings

    def _save_settings(self):
        """保存设置"""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.settings_path, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)

    def _get_default_save_directory(self):
        """获取默认保存目录"""
        system = sys.platform
        
        if system == 'win32':
            # Windows: 桌面或 C 盘
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            if os.path.exists(desktop):
                return desktop
            return 'C:\\'
        elif system == 'darwin':
            # macOS: 桌面或用户主目录
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            if os.path.exists(desktop):
                return desktop
            return os.path.expanduser('~')
        else:
            # Linux/其他: 桌面或 home 目录
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            if os.path.exists(desktop):
                return desktop
            return os.path.expanduser('~')

    def show_settings(self):
        """显示设置菜单"""
        print("=" * 60)
        print("开发者模式 - 设置")
        print("=" * 60)
        print()

        while True:
            print("\n当前设置:")
            print(f"  [1] 保存目录: {self.settings['save_directory']}")
            print(f"  [2] 自动保存到配置目录: {'是' if self.settings['auto_save_to_config_dir'] else '否'}")
            print("\n操作:")
            print("  输入数字修改设置")
            print("  输入 'r' 重置为默认")
            print("  输入 'q' 返回主菜单")

            choice = input("\n请选择: ").strip().lower()

            if choice == 'q':
                break
            elif choice == 'r':
                self.settings['save_directory'] = self._get_default_save_directory()
                self.settings['auto_save_to_config_dir'] = False
                self._save_settings()
                print("\n✓ 设置已重置为默认值")
            elif choice == '1':
                new_dir = input(f"\n请输入新的保存目录 [当前: {self.settings['save_directory']}]: ").strip()
                if new_dir:
                    new_dir = os.path.expanduser(new_dir)
                    if os.path.isdir(new_dir):
                        self.settings['save_directory'] = new_dir
                        self._save_settings()
                        print(f"\n✓ 保存目录已更新为: {new_dir}")
                    else:
                        print("\n✗ 目录不存在，请检查路径")
            elif choice == '2':
                current = self.settings['auto_save_to_config_dir']
                self.settings['auto_save_to_config_dir'] = not current
                self._save_settings()
                status = '是' if self.settings['auto_save_to_config_dir'] else '否'
                print(f"\n✓ 自动保存到配置目录已设置为: {status}")

    def authenticate(self) -> bool:
        """
        认证开发者身份

        Returns:
            是否认证成功
        """
        print("=" * 60)
        print("开发者模式认证")
        print("=" * 60)
        print()

        # 尝试使用 Tkinter 输入密码
        password = self._get_password_via_tkinter()

        # 如果 Tkinter 失败，使用终端输入
        if not password:
            print("Tkinter 窗口已关闭，请在终端输入密码：")
            password = getpass.getpass("请输入开发者密码: ")

        # 验证密码
        if password in self.DEVELOPER_PASSWORDS:
            self.authenticated = True
            print()
            print("✓ 认证成功！")
            print()
            return True
        else:
            print()
            print("✗ 认证失败：密码错误")
            print()
            return False

    def _get_password_via_tkinter(self) -> Optional[str]:
        """
        使用 Tkinter 获取密码

        Returns:
            密码或 None
        """
        try:
            # 创建 Tkinter 根窗口
            root = tk.Tk()
            root.title("r321f 开发者认证")
            root.geometry("400x200")

            # 居中显示
            root.eval('tk::PlaceWindow . center')

            # 密码输入对话框
            password = simpledialog.askstring(
                "开发者认证",
                "请输入开发者密码：",
                show='*',
                parent=root
            )

            # 销毁窗口
            root.destroy()

            return password

        except Exception as e:
            print(f"Tkinter 错误: {e}")
            return None

    def list_developer_files(self, page: int = 0, per_page: int = 5) -> List[Dict]:
        """
        列出开发者文件

        Args:
            page: 页码（从0开始）
            per_page: 每页显示数量

        Returns:
            文件列表
        """
        if not self.authenticated:
            raise PermissionError("未认证，请先使用开发者密码登录")

        # 加载开发者文件
        files = self._load_developer_files()

        # 分页
        start = page * per_page
        end = start + per_page
        return files[start:end]

    def add_developer_file(self, name: str, content: str, description: str = ""):
        """
        添加开发者文件（注意：此功能仅在开发时有效，打包后无法添加）

        Args:
            name: 文件名
            content: 文件内容
            description: 描述
        """
        if not self.authenticated:
            raise PermissionError("未认证，请先使用开发者密码登录")

        print(f"注意：打包后无法添加新文件，请在开发时直接添加到 data 目录")
        print(f"文件 '{name}' 信息已记录（未实际保存）")

    def get_developer_file(self, file_id: int) -> Optional[Dict]:
        """
        获取开发者文件

        Args:
            file_id: 文件ID

        Returns:
            文件内容或 None
        """
        if not self.authenticated:
            raise PermissionError("未认证，请先使用开发者密码登录")

        files = self._load_developer_files()

        for file in files:
            if file['id'] == file_id:
                return file

        return None

    def delete_developer_file(self, file_id: int):
        """
        删除开发者文件（注意：此功能仅在开发时有效，打包后无法删除）

        Args:
            file_id: 文件ID
        """
        if not self.authenticated:
            raise PermissionError("未认证，请先使用开发者密码登录")

        print(f"注意：打包后无法删除文件，请在开发时直接从 data 目录删除")
        print(f"文件 ID {file_id} 信息已记录（未实际删除）")

    def _load_developer_files(self) -> List[Dict]:
        """加载开发者文件"""
        # 优先使用用户配置目录中的 data 目录
        user_data_dir = os.path.join(self.config_dir, 'data')
        
        # 系统安装的 data 目录
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'data'),
            os.path.join(os.path.dirname(__file__), 'data'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'),
        ]

        system_data_dir = None
        for path in possible_paths:
            if os.path.exists(path):
                system_data_dir = path
                break

        # 如果用户配置目录不存在，创建它
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir, exist_ok=True)
            # 如果系统目录存在，复制默认文件到用户目录
            if system_data_dir and os.path.exists(system_data_dir):
                import shutil
                try:
                    for filename in os.listdir(system_data_dir):
                        src = os.path.join(system_data_dir, filename)
                        dst = os.path.join(user_data_dir, filename)
                        if not os.path.exists(dst):
                            shutil.copy2(src, dst)
                except Exception:
                    pass

        # 自动扫描用户 data 目录中的所有文件
        files = []
        if os.path.exists(user_data_dir):
            file_list = os.listdir(user_data_dir)
            file_list.sort()  # 按文件名排序

            for idx, filename in enumerate(file_list, 1):
                file_path = os.path.join(user_data_dir, filename)
                if os.path.isfile(file_path):
                    # 根据文件扩展名生成描述
                    ext = os.path.splitext(filename)[1].lower()
                    if ext == '.r321f':
                        base_name = os.path.splitext(filename)[0]
                        description = f'加密文件 ({base_name})'
                    elif ext == '.txt':
                        description = '文本文件'
                    elif ext == '.json':
                        description = 'JSON 配置文件'
                    else:
                        description = f'{ext[1:].upper()} 文件' if ext else '文件'

                    files.append({
                        'id': idx,
                        'name': filename,
                        'description': description,
                        'file_path': file_path,
                        'created_at': datetime.now().isoformat(),
                        'author': 'system'
                    })

        return files

    def run_interactive_mode(self):
        """运行交互式开发者模式"""
        if not self.authenticate():
            return

        print("=" * 60)
        print("开发者模式 - 内置加密文件")
        print("=" * 60)
        print()
        print("操作说明：")
        print("  输入数字选择文件并解密保存")
        print("  输入 'a' 或 'd' 切换上一页")
        print("  输入 'w' 或 's' 切换下一页")
        print("  输入 's' 进入设置")
        print("  输入 'q' 退出")
        print()

        current_page = 0
        per_page = 5

        while True:
            # 显示当前页文件
            files = self.list_developer_files(current_page, per_page)

            print(f"【第 {current_page + 1} 页】")
            print("-" * 60)

            if not files:
                print("没有文件")
            else:
                for file in files:
                    print(f"  [{file['id']}] {file['name']}")
                    print(f"      {file['description']}")
                    print(f"      创建时间: {file['created_at'][:10]}")
                    print()

            print("-" * 60)
            print("操作: ", end='', flush=True)

            # 获取用户输入
            try:
                choice = input().strip().lower()

                if choice == 'q':
                    print("退出开发者模式")
                    break
                elif choice in ['a', 'd']:
                    # 上一页
                    if current_page > 0:
                        current_page -= 1
                    else:
                        print("已经是第一页了")
                elif choice in ['w', 's']:
                    # 下一页
                    total_files = len(self._load_developer_files())
                    if (current_page + 1) * per_page < total_files:
                        current_page += 1
                    else:
                        print("已经是最后一页了")
                elif choice == 'set':
                    # 进入设置
                    self.show_settings()
                elif choice.isdigit():
                    # 读取并保存文件
                    file_id = int(choice)
                    file = self.get_developer_file(file_id)
                    if file:
                        print()
                        print("=" * 60)
                        print(f"正在读取文件: {file['name']}")
                        print("-" * 60)

                        try:
                            # 检查是否是加密文件
                            is_encrypted = file['name'].endswith('.r321f')

                            if file['file_path'] and os.path.exists(file['file_path']):
                                if is_encrypted:
                                    # 加密文件：使用解密器解密
                                    from ..core.decryptor import FileDecryptor
                                    from ..core.encryption_levels import get_encryption_level, get_level_config

                                    # 检查加密级别
                                    with open(file['file_path'], 'rb') as f:
                                        encrypted_data = f.read()

                                    metadata_length = int.from_bytes(encrypted_data[:4], byteorder='big')
                                    metadata_json = encrypted_data[4:4+metadata_length]
                                    metadata = json.loads(metadata_json.decode('utf-8'))

                                    encryption_level_str = metadata.get("encryption_level") or metadata.get("l", "P1")
                                    encryption_level = get_encryption_level(encryption_level_str)
                                    config = get_level_config(encryption_level)
                                    requires_password = config.get("requires_password", True)

                                    if requires_password:
                                        print("✗ 此文件需要密码，无法在开发者模式中自动解密")
                                        print("  请使用 r321f decrypt 命令手动解密")
                                    else:
                                        # P-2 级别，无需密码
                                        # 读取加密文件内容
                                        with open(file['file_path'], 'rb') as f:
                                            encrypted_data = f.read()
                                        
                                        # 使用临时文件进行解密
                                        import tempfile
                                        with tempfile.NamedTemporaryFile(delete=False, suffix='.r321f') as tmp:
                                            tmp.write(encrypted_data)
                                            tmp_path = tmp.name
                                        
                                        try:
                                            decryptor = FileDecryptor(password=None)
                                            output_path = decryptor.decrypt_file(tmp_path)
                                            
                                            # 获取保存目录
                                            if self.settings['auto_save_to_config_dir']:
                                                save_dir = self.config_dir
                                            else:
                                                save_dir = self.settings['save_directory']
                                            
                                            # 确保目录存在
                                            os.makedirs(save_dir, exist_ok=True)
                                            
                                            # 修复文件名（从元数据中获取原始文件名）
                                            try:
                                                with open(file['file_path'], 'rb') as f:
                                                    encrypted_data = f.read()
                                                metadata_length = int.from_bytes(encrypted_data[:4], byteorder='big')
                                                metadata_json = encrypted_data[4:4+metadata_length]
                                                metadata = json.loads(metadata_json.decode('utf-8'))
                                                original_filename = metadata.get('t', '').lstrip('.')
                                                if not original_filename:
                                                    original_filename = os.path.splitext(file['name'])[0]
                                            except:
                                                original_filename = os.path.splitext(file['name'])[0]
                                            
                                            # 保存到配置目录
                                            final_output = os.path.join(save_dir, original_filename)
                                            shutil.copy2(output_path, final_output)
                                            
                                            print(f"✓ 文件已解密并保存到: {final_output}")
                                            print(f"  原始文件: {file['name']}")
                                        finally:
                                            # 清理临时文件
                                            try:
                                                os.unlink(tmp_path)
                                            except:
                                                pass
                                else:
                                    # 普通文件（可能是二进制或文本）
                                    # 先尝试以文本模式读取，如果失败则以二进制模式读取
                                    try:
                                        with open(file['file_path'], 'r', encoding='utf-8') as f:
                                            content = f.read()
                                        
                                        # 获取保存目录
                                        if self.settings['auto_save_to_config_dir']:
                                            save_dir = self.config_dir
                                        else:
                                            save_dir = self.settings['save_directory']
                                        
                                        # 确保目录存在
                                        os.makedirs(save_dir, exist_ok=True)
                                        
                                        # 保存到配置目录（文本模式）
                                        output_path = os.path.join(save_dir, file['name'])
                                        with open(output_path, 'w', encoding='utf-8') as f:
                                            f.write(content)

                                        print(f"✓ 文件已保存到: {output_path}")
                                        print()
                                        print("文件内容预览:")
                                        print("-" * 60)
                                        print(content[:200] + "..." if len(content) > 200 else content)
                                        print("-" * 60)
                                    except UnicodeDecodeError:
                                        # 二进制文件，以二进制模式复制
                                        # 获取保存目录
                                        if self.settings['auto_save_to_config_dir']:
                                            save_dir = self.config_dir
                                        else:
                                            save_dir = self.settings['save_directory']
                                        
                                        # 确保目录存在
                                        os.makedirs(save_dir, exist_ok=True)
                                        
                                        output_path = os.path.join(save_dir, file['name'])
                                        with open(file['file_path'], 'rb') as src:
                                            with open(output_path, 'wb') as dst:
                                                dst.write(src.read())

                                        print(f"✓ 二进制文件已保存到: {output_path}")
                                        print(f"  文件大小: {os.path.getsize(output_path)} 字节")
                            else:
                                print(f"✗ 文件未找到: {file['name']}")

                        except Exception as e:
                            print(f"✗ 处理失败: {e}")
                            import traceback
                            traceback.print_exc()

                        print()
                        input("按 Enter 继续...")
                    else:
                        print(f"文件 ID {file_id} 不存在")
                else:
                    print("无效输入")

            except KeyboardInterrupt:
                print("\n退出开发者模式")
                break
            except Exception as e:
                print(f"错误: {e}")
