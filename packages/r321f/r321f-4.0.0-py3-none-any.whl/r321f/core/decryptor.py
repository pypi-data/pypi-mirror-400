"""
文件解密器 - 支持多种文件格式解密和5个加密级别
"""

import os
import base64
import json
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .encryption_levels import EncryptionLevel, get_level_config


class FileDecryptor:
    """文件解密器类"""

    def __init__(self, password=None, key_file=None):
        """
        初始化解密器

        Args:
            password: 解密密码
            key_file: 密钥文件路径
        """
        self.password = password
        self.key_file = key_file
        self.fernet = None
        self.metadata = None

        if password:
            # 延迟初始化，需要先读取文件获取元数据
            pass
        elif key_file:
            self._init_from_key_file(key_file)

    def _init_from_key_file(self, key_file):
        """从密钥文件初始化解密器"""
        with open(key_file, 'rb') as f:
            key = f.read()
        self.fernet = Fernet(key)

    def _init_from_password(self, password, salt, iterations):
        """
        从密码初始化解密器

        Args:
            password: 解密密码
            salt: 盐值
            iterations: 迭代次数
        """
        # 使用PBKDF2从密码派生密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(key)

    def decrypt_file(self, input_path, output_path=None, output_dir=None):
        """
        解密文件

        Args:
            input_path: 输入文件路径（加密文件）
            output_path: 输出文件路径（可选）
            output_dir: 输出目录（可选）

        Returns:
            解密后的文件路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"文件不存在: {input_path}")

        # 读取加密文件
        with open(input_path, 'rb') as f:
            encrypted_data = f.read()

        # 解析输出数据并解密
        decrypted_data = self._decrypt_data(encrypted_data, self.password)

        # 生成输出路径
        if output_path:
            pass  # 使用指定的输出路径
        elif output_dir:
            filename = os.path.basename(input_path)
            if filename.endswith('.r321f'):
                filename = filename[:-6]  # 移除.r321f后缀
            output_path = os.path.join(output_dir, filename)
        else:
            output_path = input_path
            if output_path.endswith('.r321f'):
                output_path = output_path[:-6]

        # 创建输出目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 保存解密文件
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

        return output_path

    def decrypt_from_text(self, encrypted_text, output_path=None, output_dir=None):
        """
        从文本解密文件

        Args:
            encrypted_text: 加密的文本（Base64编码）
            output_path: 输出文件路径（可选）
            output_dir: 输出目录（可选）

        Returns:
            解密后的文件路径
        """
        # 从Base64解码
        encrypted_data = base64.b64decode(encrypted_text.encode('utf-8'))

        # 解密数据
        decrypted_data = self._decrypt_data(encrypted_data, self.password)

        # 生成输出路径
        if not output_path:
            if output_dir:
                output_path = os.path.join(output_dir, 'decrypted_file')
            else:
                output_path = 'decrypted_file'

        # 创建输出目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 保存解密文件
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

        return output_path

    def _decrypt_data(self, encrypted_data, password):
        """
        解密数据

        Args:
            encrypted_data: 加密的数据（包含元数据）
            password: 解密密码

        Returns:
            解密后的数据

        Raises:
            ValueError: 解密失败
        """
        try:
            # 解析元数据长度
            metadata_length = int.from_bytes(encrypted_data[:4], byteorder='big')

            # 解析元数据
            metadata_json = encrypted_data[4:4+metadata_length]
            self.metadata = json.loads(metadata_json.decode('utf-8'))

            # 提取盐值和加密数据
            offset = 4 + metadata_length

            # 检查是否有盐值（根据版本）
            version = self.metadata.get("version") or self.metadata.get("v")
            encryption_level = self.metadata.get("encryption_level") or self.metadata.get("l")

            if version == "2.0":
                # P-2 级别：无密码，仅 base64 编码
                if encryption_level == "P-2":
                    encrypted_content = encrypted_data[offset:]
                    # 直接 base64 解码
                    decrypted_data = base64.b64decode(encrypted_content)
                    return decrypted_data

                # P-1 级别没有盐值
                elif encryption_level == "P-1":
                    salt = b''
                    encrypted_content = encrypted_data[offset:]
                else:
                    salt = encrypted_data[offset:offset+16]
                    encrypted_content = encrypted_data[offset+16:]
            else:
                # 旧版本兼容
                salt = encrypted_data[offset:offset+16] if len(encrypted_data) > offset + 16 else b''
                encrypted_content = encrypted_data[offset+16:] if salt else encrypted_data[offset:]

            # 如果使用密码，初始化解密器
            if password and not self.fernet:
                iterations = self.metadata.get("iterations", 100000)
                self._init_from_password(password, salt, iterations)

            # 解密数据
            decrypted_data = self.fernet.decrypt(encrypted_content)

            return decrypted_data

        except InvalidToken as e:
            raise ValueError(f"解密失败：密码错误或密钥不匹配") from e
        except json.JSONDecodeError as e:
            raise ValueError(f"解密失败：文件格式错误或已损坏") from e
        except Exception as e:
            raise ValueError(f"解密失败：{str(e)}") from e