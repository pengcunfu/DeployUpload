#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeployUpload 安装配置文件
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# 读取requirements文件
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="deployupload",
    version="1.0.0",
    author="pengcunfu",
    author_email="3173484026@qq.com",
    description="一个用于将本地文件夹打包并上传到远程服务器的Python包",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/pengcunfu/DeployUpload",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-mock>=3.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
            "tox>=3.0",
            "build>=0.7.0",
            "twine>=3.0",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-mock>=3.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "deployupload=deployupload.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
