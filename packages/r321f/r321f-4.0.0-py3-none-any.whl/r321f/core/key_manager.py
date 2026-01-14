"""
密钥管理器 - 支持双重认证密钥生成，修复明文存储漏洞
"""

import os
import json
import base64
import hashlib
import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from datetime import datetime


class KeyManager:
    """密钥管理器类"""

    def __init__(self, storage_dir=None, master_password=None):
        """
        初始化密钥管理器

        Args:
            storage_dir: 密钥存储目录
            master_password: 主密码（用于加密密钥文件）
        """
        if storage_dir is None:
            # 默认存储目录
            home = os.path.expanduser('~')
            self.storage_dir = os.path.join(home, '.r321f', 'keys')
        else:
            self.storage_dir = storage_dir

        self.master_password = master_password

        # 创建存储目录
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)

    def generate_key(self):
        """
        生成新的Fernet密钥

        Returns:
            密钥（字节）
        """
        return Fernet.generate_key()

    def generate_dual_auth_key(self, password1, password2):
        """
        生成双重认证密钥

        Args:
            password1: 第一个密码
            password2: 第二个密码

        Returns:
            密钥（字节）
        """
        # 使用两个密码的组合生成密钥
        combined = password1 + '\x00' + password2  # 使用空字符分隔，避免冒号冲突

        # 生成随机盐值
        salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=200000,  # 更高的迭代次数增加安全性
        )
        key = base64.urlsafe_b64encode(kdf.derive(combined.encode()))

        return key

    def generate_file_type_key(self, password, file_extension):
        """
        根据文件类型生成特定密钥

        Args:
            password: 密码
            file_extension: 文件扩展名（如 '.zip', '.docx'）

        Returns:
            密钥（字节）
        """
        # 将文件扩展名作为盐值的一部分，并添加随机盐
        base_salt = f'r321f_{file_extension}_salt'.encode()
        random_salt = os.urandom(16)
        salt = base_salt + random_salt

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

        return key

    def save_key(self, key, key_name, metadata=None, encrypt_with_master=True):
        """
        保存密钥到文件（加密存储）

        Args:
            key: 密钥（字节）
            key_name: 密钥名称
            metadata: 元数据（字典）
            encrypt_with_master: 是否使用主密码加密
        """
        key_path = os.path.join(self.storage_dir, f'{key_name}.key')

        # 准备密钥信息
        key_info = {
            'key': base64.b64encode(key).decode('utf-8'),
            'created_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        # 序列化密钥信息
        key_json = json.dumps(key_info, indent=2).encode('utf-8')

        # 如果有主密码，加密密钥文件
        if encrypt_with_master and self.master_password:
            # 生成随机盐值
            salt = os.urandom(16)

            # 使用主密码派生加密密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            encryption_key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))

            # 加密密钥数据
            fernet = Fernet(encryption_key)
            encrypted_key_data = fernet.encrypt(key_json)

            # 保存加密的密钥文件（格式: [盐值16字节][加密数据]）
            with open(key_path, 'wb') as f:
                f.write(salt + encrypted_key_data)
        else:
            # 不加密，直接保存（不推荐）
            with open(key_path, 'w', encoding='utf-8') as f:
                f.write(key_json.decode('utf-8'))

        return key_path

    def load_key(self, key_name, master_password=None):
        """
        从文件加载密钥

        Args:
            key_name: 密钥名称
            master_password: 主密码（如果密钥文件已加密）

        Returns:
            密钥（字节）
        """
        key_path = os.path.join(self.storage_dir, f'{key_name}.key')

        if not os.path.exists(key_path):
            raise FileNotFoundError(f"密钥文件不存在: {key_path}")

        # 尝试读取文件
        with open(key_path, 'rb') as f:
            data = f.read()

        # 检查是否是加密的密钥文件
        if len(data) > 16:
            # 尝试解密
            try:
                salt = data[:16]
                encrypted_data = data[16:]

                # 使用主密码派生解密密钥
                pwd = master_password or self.master_password
                if not pwd:
                    pwd = getpass.getpass("请输入主密码以解密密钥文件: ")

                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                encryption_key = base64.urlsafe_b64encode(kdf.derive(pwd.encode()))

                # 解密密钥数据
                fernet = Fernet(encryption_key)
                decrypted_data = fernet.decrypt(encrypted_data)

                # 解析JSON
                key_info = json.loads(decrypted_data.decode('utf-8'))
            except Exception:
                # 解密失败，尝试作为明文读取
                try:
                    key_info = json.loads(data.decode('utf-8'))
                except json.JSONDecodeError:
                    raise ValueError("密钥文件格式错误或密码不正确")
        else:
            # 明文文件
            key_info = json.loads(data.decode('utf-8'))

        key = base64.b64decode(key_info['key'].encode('utf-8'))

        return key

    def list_keys(self):
        """
        列出所有密钥

        Returns:
            密钥列表
        """
        keys = []

        if not os.path.exists(self.storage_dir):
            return keys

        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.key'):
                key_name = filename[:-4]
                key_path = os.path.join(self.storage_dir, filename)

                try:
                    # 尝试读取密钥信息
                    with open(key_path, 'rb') as f:
                        data = f.read()

                    # 检查是否加密
                    if len(data) > 16:
                        try:
                            salt = data[:16]
                            encrypted_data = data[16:]

                            # 尝试解密
                            if self.master_password:
                                kdf = PBKDF2HMAC(
                                    algorithm=hashes.SHA256(),
                                    length=32,
                                    salt=salt,
                                    iterations=100000,
                                )
                                encryption_key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
                                fernet = Fernet(encryption_key)
                                decrypted_data = fernet.decrypt(encrypted_data)
                                key_info = json.loads(decrypted_data.decode('utf-8'))
                            else:
                                # 无法解密，只显示基本信息
                                key_info = {
                                    'created_at': 'Unknown (encrypted)',
                                    'metadata': {'encrypted': True}
                                }
                        except Exception:
                            key_info = {
                                'created_at': 'Unknown (encrypted)',
                                'metadata': {'encrypted': True}
                            }
                    else:
                        key_info = json.loads(data.decode('utf-8'))

                    keys.append({
                        'name': key_name,
                        'created_at': key_info.get('created_at'),
                        'metadata': key_info.get('metadata', {})
                    })
                except Exception:
                    # 跳过损坏的密钥文件
                    continue

        return keys

    def delete_key(self, key_name):
        """
        删除密钥

        Args:
            key_name: 密钥名称
        """
        key_path = os.path.join(self.storage_dir, f'{key_name}.key')

        if os.path.exists(key_path):
            os.remove(key_path)
            return True

        return False

    def encrypt_key_file(self, key, password, output_path):
        """
        加密密钥文件（用于内置密钥功能）

        Args:
            key: 要加密的密钥
            password: 保护密码
            output_path: 输出文件路径
        """
        # 生成随机盐值
        salt = os.urandom(16)

        # 使用密码派生密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        encryption_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

        # 加密密钥
        fernet = Fernet(encryption_key)
        encrypted_key = fernet.encrypt(key)

        # 保存加密的密钥文件（格式: [盐值16字节][加密数据]）
        with open(output_path, 'wb') as f:
            f.write(salt + encrypted_key)

    def decrypt_key_file(self, encrypted_key_path, password):
        """
        解密密钥文件（用于内置密钥功能）

        Args:
            encrypted_key_path: 加密的密钥文件路径
            password: 保护密码

        Returns:
            解密后的密钥
        """
        # 读取加密的密钥
        with open(encrypted_key_path, 'rb') as f:
            data = f.read()

        # 提取盐值和加密数据
        salt = data[:16]
        encrypted_key = data[16:]

        # 使用密码派生密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        encryption_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

        # 解密密钥
        fernet = Fernet(encryption_key)
        key = fernet.decrypt(encrypted_key)

        return key