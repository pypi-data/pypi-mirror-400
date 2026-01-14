"""
r321f 安装配置文件
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

setup(
    name='r321f',
    version='4.0.0',
    author='ruin321',
    description='文件加密解密工具 - 支持多种文件格式',
    long_description=read_file('README.md') if os.path.exists('README.md') else '文件加密解密工具，支持压缩包、文档、Office文档、可执行程序等多种文件格式的加密解密',
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'cryptography>=41.0.0',
    ],
    entry_points={
        'console_scripts': [
            'r321f=r321f.cli.main:main',
            'r321f-np=r321f.cli.main:main',
            'r321f-tui=r321f.cli.tui:main',
            'r321f-CRonly=r321f.cli.cr_only:main',
        ],
    },
    keywords='encryption decryption security file crypto',
)
