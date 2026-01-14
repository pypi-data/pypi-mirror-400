# r321f - 文件加密解密工具

r321f 是一个强大的文件加密解密工具，支持多种文件格式，包括压缩包、文档、Office文档、可执行程序等。

## 功能特性

- ✅ 支持多种文件格式加密解密（ZIP、PDF、DOCX、XLSX、EXE等）
- ✅ 支持密码加密和密钥文件加密
- ✅ 支持双重认证密钥生成
- ✅ 支持文件类型特定密钥
- ✅ 支持加密为文本格式
- ✅ 支持从文本解密
- ✅ 支持自定义输出目录
- ✅ 内置密钥管理功能（r321f-np）
- ✅ 跨平台支持（Windows、macOS、Linux）
- ✅ 命令行和Python API两种使用方式

## 安装

### 使用pip安装

```bash
pip install r321f
```

### 从源码安装

```bash
git clone https://github.com/r321f/r321f.git
cd r321f
pip install -e .
```

## 快速开始

### 命令行使用

#### 1. 基本加密

```bash
# 加密文件（会提示输入密码）
r321f encrypt document.pdf

# 加密文件到指定输出路径
r321f encrypt document.pdf -o encrypted.r321f

# 加密文件到指定目录
r321f encrypt document.pdf -d /path/to/output
```

#### 2. 基本解密

```bash
# 解密文件（会提示输入密码）
r321f decrypt encrypted.r321f

# 解密文件到指定输出路径
r321f decrypt encrypted.r321f -o document.pdf

# 解密文件到指定目录
r321f decrypt encrypted.r321f -d /path/to/output
```

#### 3. 加密为文本

```bash
# 加密文件并输出为文本（显示在终端）
r321f encrypt document.pdf --text
```

#### 4. 从文本解密

```bash
# 从文本解密（需要复制加密的文本）
r321f decrypt --text "encrypted_text_here" -o document.pdf
```

#### 5. 使用密钥文件

```bash
# 生成密钥
r321f key generate mykey

# 使用密钥文件加密
r321f encrypt document.pdf -k ~/.r321f/keys/mykey.key

# 使用密钥文件解密
r321f decrypt encrypted.r321f -k ~/.r321f/keys/mykey.key
```

#### 6. 双重认证

```bash
# 使用双重认证加密（需要输入两个密码）
r321f encrypt document.pdf --dual-auth

# 使用双重认证解密
r321f decrypt encrypted.r321f --dual-auth
```

#### 7. 文件类型特定密钥

```bash
# 使用文件类型特定密钥加密
r321f encrypt document.pdf --file-type-key

# 使用文件类型特定密钥解密
r321f decrypt encrypted.r321f --file-type-key
```

#### 8. 内置密钥功能（r321f-np）

```bash
# 初始化内置密钥（会提示输入保护密码）
r321f-np --init

# 解密内置密钥文件到C盘（Windows）或用户目录（macOS/Linux）
r321f-np --decrypt
```

### Python API使用

#### 1. 基本加密解密

```python
from r321f import FileEncryptor, FileDecryptor

# 使用密码加密
encryptor = FileEncryptor(password='mypassword')
output_path = encryptor.encrypt_file('document.pdf')
print(f"加密成功: {output_path}")

# 使用密码解密
decryptor = FileDecryptor(password='mypassword')
output_path = decryptor.decrypt_file('document.pdf.r321f')
print(f"解密成功: {output_path}")
```

#### 2. 加密为文本

```python
from r321f import FileEncryptor

encryptor = FileEncryptor(password='mypassword')
encrypted_text = encryptor.encrypt_to_text('document.pdf')
print(f"加密后的文本: {encrypted_text}")
```

#### 3. 从文本解密

```python
from r321f import FileDecryptor

decryptor = FileDecryptor(password='mypassword')
output_path = decryptor.decrypt_from_text(encrypted_text, 'document.pdf')
print(f"解密成功: {output_path}")
```

#### 4. 使用密钥文件

```python
from r321f import FileEncryptor, FileDecryptor, KeyManager

# 生成密钥
key_manager = KeyManager()
key = key_manager.generate_key()
key_path = key_manager.save_key(key, 'mykey')

# 使用密钥文件加密
encryptor = FileEncryptor(key_file=key_path)
output_path = encryptor.encrypt_file('document.pdf')

# 使用密钥文件解密
decryptor = FileDecryptor(key_file=key_path)
output_path = decryptor.decrypt_file('document.pdf.r321f')
```

#### 5. 双重认证

```python
from r321f import FileEncryptor, FileDecryptor, KeyManager

# 生成双重认证密钥
key_manager = KeyManager()
key = key_manager.generate_dual_auth_key('password1', 'password2')

# 使用Fernet加密器
from cryptography.fernet import Fernet
fernet = Fernet(key)

# 加密
with open('document.pdf', 'rb') as f:
    data = f.read()
encrypted = fernet.encrypt(data)

with open('document.pdf.r321f', 'wb') as f:
    f.write(encrypted)

# 解密
with open('document.pdf.r321f', 'rb') as f:
    encrypted_data = f.read()
decrypted = fernet.decrypt(encrypted_data)

with open('document.pdf', 'wb') as f:
    f.write(decrypted)
```

#### 6. 文件类型特定密钥

```python
from r321f import FileEncryptor, FileDecryptor, KeyManager

# 生成文件类型特定密钥
key_manager = KeyManager()
key = key_manager.generate_file_type_key('mypassword', '.pdf')

from cryptography.fernet import Fernet
fernet = Fernet(key)

# 加密
with open('document.pdf', 'rb') as f:
    data = f.read()
encrypted = fernet.encrypt(data)

with open('document.pdf.r321f', 'wb') as f:
    f.write(encrypted)
```

## 高级功能

### 密钥管理

```bash
# 列出所有密钥
r321f key list

# 删除密钥
r321f key delete mykey
```

### 支持的文件格式

r321f 支持加密任何类型的文件，包括但不限于：

- **压缩文件**: ZIP, RAR, 7Z, TAR, GZ
- **文档**: PDF, TXT, DOC, DOCX
- **表格**: XLS, XLSX, CSV
- **演示文稿**: PPT, PPTX
- **图片**: JPG, PNG, GIF, BMP
- **音频**: MP3, WAV, FLAC
- **视频**: MP4, AVI, MKV
- **可执行程序**: EXE, APP, BIN
- **代码文件**: PY, JS, JAVA, C, CPP等

### 内置密钥功能详解

内置密钥功能（r321f-np）提供了一个安全的密钥存储方案：

1. **初始化**: `r321f-np --init`
   - 创建一个加密的密钥文件
   - 使用保护密码加密密钥
   - 自动保存到平台特定位置（C盘/用户目录）

2. **解密**: `r321f-np --decrypt`
   - 使用保护密码解密密钥文件
   - 将解密后的密钥保存到指定位置
   - 可用于后续的加密解密操作

### 服务器功能

服务器功能正在开发中，未来版本将支持：

- 上传加密文件到服务器
- 从服务器下载加密文件
- 服务器端密钥管理

## 平台支持

r321f 支持：

- ✅ Windows 7/8/10/11
- ✅ macOS 10.12+
- ✅ Linux (Ubuntu, Debian, CentOS, Fedora, Arch等)
- ✅ Android (通过Termux)

## 安全性

- 使用 AES-128 加密算法（通过Fernet）
- 密码使用 PBKDF2 派生，增加安全性
- 支持双重认证，提高安全性
- 密钥文件加密存储

## 常见问题

### Q: 忘记密码怎么办？

A: r321f 使用强加密算法，没有密码无法解密文件。请务必妥善保管密码。

### Q: 支持哪些加密算法？

A: r321f 使用 Fernet（基于AES-128-CBC）进行加密。

### Q: 可以加密大文件吗？

A: 可以，但建议对于非常大的文件（>1GB），可能需要优化内存使用。

### Q: 加密后的文件可以跨平台使用吗？

A: 可以，加密后的文件可以在任何支持r321f的平台上解密。

## 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- GitHub: https://github.com/r321f/r321f
- Email: support@r321f.com

## 更新日志

### v4.0.0 (2026-01-09)

- 版本升级到 4.0.0
- 支持多种文件格式加密解密
- 支持密码和密钥文件加密
- 支持双重认证
- 支持文件类型特定密钥
- 支持加密为文本格式
- 支持内置密钥管理
- 跨平台支持（Windows、macOS、Linux）