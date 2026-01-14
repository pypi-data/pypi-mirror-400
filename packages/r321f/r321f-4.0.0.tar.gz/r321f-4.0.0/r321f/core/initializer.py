"""
初始化模块 - 处理 r321f init 功能
"""

import os
import sys
import platform
import subprocess
import getpass
import json
from datetime import datetime
from .key_manager import KeyManager


class R321FInitializer:
    """r321f 初始化器"""

    def __init__(self):
        self.home_dir = os.path.expanduser('~')
        self.config_dir = os.path.join(self.home_dir, '.r321f')
        self.config_file = os.path.join(self.config_dir, 'config.json')
        self.initialized = False

    def is_initialized(self):
        """检查是否已初始化"""
        return os.path.exists(self.config_file)

    def run_init(self, force=False, skip_network_check=False):
        """
        运行初始化流程

        Args:
            force: 强制重新初始化
            skip_network_check: 跳过网络检查
        """
        if self.is_initialized() and not force:
            print("r321f 已经初始化完成！")
            print("如需重新初始化，请使用: r321f init --force")
            return

        print("=" * 60)
        print("r321f 初始化向导")
        print("=" * 60)
        print()

        # 步骤1: 安全检查
        print("【步骤 1/5】安全环境检查")
        print("-" * 60)
        self._security_check(skip_network_check)
        print()

        # 步骤2: 创建配置目录
        print("【步骤 2/5】创建配置目录")
        print("-" * 60)
        self._create_directories()
        print()

        # 步骤3: 设置主密码
        print("【步骤 3/5】设置主密码")
        print("-" * 60)
        master_password = self._setup_master_password()
        print()

        # 步骤4: 生成初始密钥
        print("【步骤 4/5】生成初始密钥")
        print("-" * 60)
        self._generate_initial_keys(master_password)
        print()

        # 步骤5: 保存配置
        print("【步骤 5/5】保存配置")
        print("-" * 60)
        self._save_config(master_password)
        print()

        # 完成
        print("=" * 60)
        print("✓ 初始化完成！")
        print("=" * 60)
        print()
        print("r321f 已成功初始化并配置。")
        print()
        print("重要提示：")
        print("  1. 请妥善保管您的主密码，丢失后无法恢复")
        print("  2. 配置文件已加密存储在: ~/.r321f/")
        print("  3. 所有密钥都已加密保护")
        print()
        print("现在可以使用以下命令：")
        print("  r321f encrypt <文件>     - 加密文件")
        print("  r321f decrypt <文件>     - 解密文件")
        print("  r321f-tui                - 启动TUI界面")
        print()

    def _security_check(self, skip_network_check):
        """安全环境检查"""
        print("正在检查系统安全状态...")

        # 检查可疑进程
        suspicious_processes = self._check_suspicious_processes()
        if suspicious_processes:
            print(f"⚠ 警告：发现 {len(suspicious_processes)} 个可疑进程：")
            for proc in suspicious_processes:
                print(f"  - {proc}")
            print()

            response = input("是否继续初始化？(y/N): ").strip().lower()
            if response != 'y':
                print("初始化已取消。")
                sys.exit(0)
        else:
            print("✓ 未发现可疑进程")

        # 网络连接检查
        if not skip_network_check:
            print()
            print("⚠ 警告：初始化过程中建议断开网络连接")
            print("  这可以防止潜在的远程攻击和数据泄露")
            print()
            response = input("是否已断开网络？(y/N): ").strip().lower()
            if response != 'y':
                print("建议先断开网络后再继续初始化。")
                print("如需跳过此检查，请使用: r321f init --skip-network-check")
                response = input("是否继续？(y/N): ").strip().lower()
                if response != 'y':
                    print("初始化已取消。")
                    sys.exit(0)

        print("✓ 安全检查通过")

    def _check_suspicious_processes(self):
        """检查可疑进程"""
        suspicious_keywords = [
            'inject', 'hook', 'debugger', 'wireshark', 'tcpdump',
            'mitmproxy', 'burpsuite', 'frida', 'xposed', 'magisk',
            'root', 'su', 'adb'
        ]

        suspicious_processes = []

        try:
            # 获取进程列表
            if platform.system() == 'Windows':
                result = subprocess.run(['tasklist'], capture_output=True, text=True)
            else:
                result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)

            if result.returncode == 0:
                processes = result.stdout.lower()
                for keyword in suspicious_keywords:
                    if keyword in processes:
                        suspicious_processes.append(keyword)
        except Exception as e:
            print(f"⚠ 无法检查进程: {e}")

        return suspicious_processes

    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.config_dir,
            os.path.join(self.config_dir, 'keys'),
            os.path.join(self.config_dir, 'temp'),
            os.path.join(self.config_dir, 'logs'),
        ]

        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"✓ 创建目录: {directory}")
            else:
                print(f"✓ 目录已存在: {directory}")

    def _setup_master_password(self):
        """设置主密码"""
        while True:
            password = getpass.getpass("请输入主密码（至少8位）: ")
            if len(password) < 8:
                print("✗ 密码长度不足，请至少输入8位")
                continue

            confirm = getpass.getpass("请再次输入主密码: ")
            if password != confirm:
                print("✗ 两次输入的密码不一致")
                continue

            # 密码强度检查
            if self._check_password_strength(password) < 2:
                print("⚠ 警告：密码强度较弱，建议使用大小写字母、数字和特殊字符的组合")
                response = input("是否继续？(y/N): ").strip().lower()
                if response != 'y':
                    continue

            print("✓ 主密码设置成功")
            return password

    def _check_password_strength(self, password):
        """检查密码强度"""
        strength = 0
        if len(password) >= 8:
            strength += 1
        if len(password) >= 12:
            strength += 1
        if any(c.isupper() for c in password):
            strength += 1
        if any(c.islower() for c in password):
            strength += 1
        if any(c.isdigit() for c in password):
            strength += 1
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            strength += 1
        return strength

    def _generate_initial_keys(self, master_password):
        """生成初始密钥"""
        key_manager = KeyManager(master_password=master_password)

        # 生成默认密钥
        default_key = key_manager.generate_key()
        key_manager.save_key(default_key, 'default', {
            'description': '默认加密密钥',
            'auto_generated': True
        })
        print("✓ 生成默认密钥")

        # 生成备份密钥
        backup_key = key_manager.generate_key()
        key_manager.save_key(backup_key, 'backup', {
            'description': '备份加密密钥',
            'auto_generated': True
        })
        print("✓ 生成备份密钥")

    def _save_config(self, master_password):
        """保存配置"""
        config = {
            'version': '2.0',
            'initialized_at': datetime.now().isoformat(),
            'platform': platform.system(),
            'encryption_level': 'P1',
            'master_password_hash': self._hash_password(master_password),
            'features': {
                'dual_auth': True,
                'file_type_key': True,
                'tui': True,
                'cr_only': True
            }
        }

        # 保存配置（加密）
        config_path = self.config_file
        key_manager = KeyManager(master_password=master_password)

        # 序列化配置
        config_json = json.dumps(config, indent=2).encode('utf-8')

        # 加密配置
        salt = os.urandom(16)
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        from cryptography.fernet import Fernet

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        encryption_key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        fernet = Fernet(encryption_key)
        encrypted_config = fernet.encrypt(config_json)

        # 保存加密配置
        with open(config_path, 'wb') as f:
            f.write(salt + encrypted_config)

        print(f"✓ 配置已保存到: {config_path}")

    def _hash_password(self, password):
        """哈希密码"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def load_config(self, master_password=None):
        """加载配置"""
        if not os.path.exists(self.config_file):
            return None

        # 读取加密配置
        with open(self.config_file, 'rb') as f:
            data = f.read()

        # 提取盐值和加密数据
        salt = data[:16]
        encrypted_config = data[16:]

        # 解密配置
        if not master_password:
            master_password = getpass.getpass("请输入主密码: ")

        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        from cryptography.fernet import Fernet

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        encryption_key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        fernet = Fernet(encryption_key)
        decrypted_config = fernet.decrypt(encrypted_config)

        return json.loads(decrypted_config.decode('utf-8'))