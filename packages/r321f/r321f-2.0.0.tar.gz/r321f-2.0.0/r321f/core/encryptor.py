"""
文件加密器 - 支持多种文件格式加密和5个加密级别
"""

import os
import base64
import json
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .encryption_levels import EncryptionLevel, get_level_config


class FileEncryptor:
    """文件加密器类"""

    def __init__(self, password=None, key_file=None, encryption_level=EncryptionLevel.P1):
        """
        初始化加密器

        Args:
            password: 加密密码
            key_file: 密钥文件路径
            encryption_level: 加密级别 (默认 P1)
        """
        self.password = password
        self.key_file = key_file
        self.encryption_level = encryption_level
        self.fernet = None
        self.salt = None
        self.config = get_level_config(encryption_level)

        if password:
            self._init_from_password(password)
        elif key_file:
            self._init_from_key_file(key_file)

    def _init_from_password(self, password):
        """从密码初始化加密器"""
        # P-2 级别不需要密码，仅使用 base64 编码
        if not self.config["requires_password"]:
            self.fernet = None
            return

        # 根据加密级别决定是否使用盐值
        if self.config["use_salt"]:
            # 生成随机盐值
            self.salt = os.urandom(16)
        elif "fixed_salt" in self.config:
            # 使用固定盐值
            self.salt = self.config["fixed_salt"]
        else:
            # P-1 级别不使用盐值
            self.salt = b''

        # 使用PBKDF2从密码派生密钥
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=self.config["iterations"],
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(key)

    def _init_from_key_file(self, key_file):
        """从密钥文件初始化加密器"""
        with open(key_file, 'rb') as f:
            key = f.read()
        self.fernet = Fernet(key)

    def encrypt_file(self, input_path, output_path=None, output_dir=None):
        """
        加密文件

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（可选）
            output_dir: 输出目录（可选）

        Returns:
            加密后的文件路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"文件不存在: {input_path}")

        # 读取文件内容（支持大文件流式处理）
        file_data = self._read_file(input_path)

        # P-2 级别：仅使用 base64 编码
        if not self.config["requires_password"]:
            encrypted_data = base64.b64encode(file_data)
        else:
            # 加密数据
            encrypted_data = self.fernet.encrypt(file_data)

        # 准备输出数据（包含元数据）
        output_data = self._prepare_output_data(encrypted_data, input_path)

        # 生成输出路径
        if output_path:
            pass  # 使用指定的输出路径
        elif output_dir:
            filename = os.path.basename(input_path) + '.r321f'
            output_path = os.path.join(output_dir, filename)
        else:
            output_path = input_path + '.r321f'

        # 创建输出目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 保存加密文件
        with open(output_path, 'wb') as f:
            f.write(output_data)

        return output_path

    def encrypt_to_text(self, input_path):
        """
        加密文件并返回文本格式

        Args:
            input_path: 输入文件路径

        Returns:
            加密后的文本（Base64编码）
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"文件不存在: {input_path}")

        # 读取文件内容
        file_data = self._read_file(input_path)

        # P-2 级别：仅使用 base64 编码
        if not self.config["requires_password"]:
            encrypted_data = base64.b64encode(file_data)
        else:
            # 加密数据
            encrypted_data = self.fernet.encrypt(file_data)

        # 准备输出数据
        output_data = self._prepare_output_data(encrypted_data, input_path)

        # 转换为Base64文本
        encrypted_text = base64.b64encode(output_data).decode('utf-8')

        return encrypted_text

    def _read_file(self, file_path, chunk_size=1024*1024):
        """
        读取文件内容（支持大文件）

        Args:
            file_path: 文件路径
            chunk_size: 块大小（默认1MB）

        Returns:
            文件内容
        """
        with open(file_path, 'rb') as f:
            return f.read()

    def _prepare_output_data(self, encrypted_data, input_path):
        """
        准备输出数据（包含盐值和元数据）

        Args:
            encrypted_data: 加密后的数据
            input_path: 输入文件路径

        Returns:
            包含盐值和元数据的输出数据
        """
        # P-2 级别：使用简化的元数据
        if not self.config["requires_password"]:
            # P-2 级别只需要最少的信息
            metadata = {
                "v": "2.0",
                "l": "P-2",
                "t": os.path.splitext(input_path)[1],
            }
        else:
            # 其他级别使用完整元数据
            metadata = {
                "version": "2.0",
                "encryption_level": self.encryption_level.value,
                "algorithm": "AES-128-CBC",
                "iterations": self.config["iterations"],
                "file_type": os.path.splitext(input_path)[1],
            }

        # 序列化元数据
        metadata_json = json.dumps(metadata).encode('utf-8')
        metadata_length = len(metadata_json).to_bytes(4, byteorder='big')

        # 构建输出数据: [元数据长度4字节][元数据][盐值16字节][加密数据]
        # P-1 和 P-2 级别不包含盐值
        if self.salt:
            output_data = metadata_length + metadata_json + self.salt + encrypted_data
        else:
            output_data = metadata_length + metadata_json + encrypted_data

        return output_data