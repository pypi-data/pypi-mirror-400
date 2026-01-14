"""
流式加密/解密 - 支持大文件处理
"""

import os
import base64
import json
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .encryption_levels import EncryptionLevel, get_level_config


class StreamEncryptor:
    """流式加密器 - 支持大文件"""

    CHUNK_SIZE = 1024 * 1024  # 1MB 块大小

    def __init__(self, password=None, key_file=None, encryption_level=EncryptionLevel.P1):
        """
        初始化流式加密器

        Args:
            password: 加密密码
            key_file: 密钥文件路径
            encryption_level: 加密级别
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
        if self.config["use_salt"]:
            self.salt = os.urandom(16)
        elif "fixed_salt" in self.config:
            self.salt = self.config["fixed_salt"]
        else:
            self.salt = b''

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

    def encrypt_file(self, input_path, output_path=None, output_dir=None, progress_callback=None):
        """
        流式加密文件

        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（可选）
            output_dir: 输出目录（可选）
            progress_callback: 进度回调函数 callback(current, total)

        Returns:
            加密后的文件路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"文件不存在: {input_path}")

        # 生成输出路径
        if output_path:
            pass
        elif output_dir:
            filename = os.path.basename(input_path) + '.r321f'
            output_path = os.path.join(output_dir, filename)
        else:
            output_path = input_path + '.r321f'

        # 创建输出目录
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 获取文件大小
        file_size = os.path.getsize(input_path)

        # 准备元数据
        metadata = {
            "version": "2.0",
            "encryption_level": self.encryption_level.value,
            "algorithm": "AES-128-CBC",
            "iterations": self.config["iterations"],
            "file_type": os.path.splitext(input_path)[1],
            "file_size": file_size,
            "chunk_size": self.CHUNK_SIZE,
        }

        # 序列化元数据
        metadata_json = json.dumps(metadata).encode('utf-8')
        metadata_length = len(metadata_json).to_bytes(4, byteorder='big')

        # 写入输出文件
        with open(output_path, 'wb') as out_file:
            # 写入元数据
            out_file.write(metadata_length + metadata_json)

            # 写入盐值
            if self.salt:
                out_file.write(self.salt)

            # 流式加密
            with open(input_path, 'rb') as in_file:
                encrypted_bytes = 0
                while True:
                    chunk = in_file.read(self.CHUNK_SIZE)
                    if not chunk:
                        break

                    # 加密块
                    encrypted_chunk = self.fernet.encrypt(chunk)
                    out_file.write(encrypted_chunk)

                    encrypted_bytes += len(chunk)

                    # 调用进度回调
                    if progress_callback:
                        progress_callback(encrypted_bytes, file_size)

        return output_path


class StreamDecryptor:
    """流式解密器 - 支持大文件"""

    CHUNK_SIZE = 1024 * 1024  # 1MB 块大小

    def __init__(self, password=None, key_file=None):
        """
        初始化流式解密器

        Args:
            password: 解密密码
            key_file: 密钥文件路径
        """
        self.password = password
        self.key_file = key_file
        self.fernet = None
        self.metadata = None

        if password:
            pass  # 延迟初始化
        elif key_file:
            self._init_from_key_file(key_file)

    def _init_from_key_file(self, key_file):
        """从密钥文件初始化解密器"""
        with open(key_file, 'rb') as f:
            key = f.read()
        self.fernet = Fernet(key)

    def _init_from_password(self, password, salt, iterations):
        """从密码初始化解密器"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(key)

    def decrypt_file(self, input_path, output_path=None, output_dir=None, progress_callback=None):
        """
        流式解密文件

        Args:
            input_path: 输入文件路径（加密文件）
            output_path: 输出文件路径（可选）
            output_dir: 输出目录（可选）
            progress_callback: 进度回调函数 callback(current, total)

        Returns:
            解密后的文件路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"文件不存在: {input_path}")

        # 读取文件头部
        with open(input_path, 'rb') as f:
            # 读取元数据长度
            metadata_length_bytes = f.read(4)
            metadata_length = int.from_bytes(metadata_length_bytes, byteorder='big')

            # 读取元数据
            metadata_json = f.read(metadata_length)
            self.metadata = json.loads(metadata_json.decode('utf-8'))

            # 读取盐值
            if self.metadata.get("encryption_level") == "P-1":
                salt = b''
            else:
                salt = f.read(16)

            # 获取加密数据起始位置
            data_start = f.tell()

        # 获取文件大小
        file_size = os.path.getsize(input_path)
        total_encrypted_size = file_size - data_start

        # 初始化解密器
        if self.password and not self.fernet:
            iterations = self.metadata.get("iterations", 100000)
            self._init_from_password(self.password, salt, iterations)

        # 生成输出路径
        if output_path:
            pass
        elif output_dir:
            filename = os.path.basename(input_path)
            if filename.endswith('.r321f'):
                filename = filename[:-6]
            output_path = os.path.join(output_dir, filename)
        else:
            output_path = input_path
            if output_path.endswith('.r321f'):
                output_path = output_path[:-6]

        # 创建输出目录
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 流式解密
        try:
            with open(input_path, 'rb') as in_file:
                # 跳过元数据和盐值
                in_file.seek(data_start)

                with open(output_path, 'wb') as out_file:
                    decrypted_bytes = 0
                    while True:
                        # Fernet 加密的数据块大小是可变的
                        # 我们需要读取一个完整的加密块
                        # Fernet 格式: [版本1字节][时间戳8字节][IV16字节][HMAC32字节][数据]

                        # 读取至少 57 字节 (1+8+16+32)
                        header = in_file.read(57)
                        if not header or len(header) < 57:
                            break

                        # 解析头部获取数据长度
                        # Fernet 使用 base64url 编码，所以我们需要找到完整的 token
                        # 简单方法：读取更多数据直到找到有效的 token

                        # 读取更多数据
                        additional_data = in_file.read(1024 * 100)  # 读取最多100KB
                        if not additional_data:
                            break

                        # 尝试解密
                        encrypted_chunk = header + additional_data

                        try:
                            decrypted_chunk = self.fernet.decrypt(encrypted_chunk)
                            out_file.write(decrypted_chunk)
                            decrypted_bytes += len(decrypted_chunk)

                            # 调用进度回调
                            if progress_callback:
                                progress_callback(decrypted_bytes, total_encrypted_size)
                        except InvalidToken:
                            # 需要更多数据，继续读取
                            continue

            return output_path

        except InvalidToken as e:
            # 删除部分解密的文件
            if os.path.exists(output_path):
                os.remove(output_path)
            raise ValueError(f"解密失败：密码错误或密钥不匹配") from e
        except Exception as e:
            # 删除部分解密的文件
            if os.path.exists(output_path):
                os.remove(output_path)
            raise ValueError(f"解密失败：{str(e)}") from e