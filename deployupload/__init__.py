#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeployUpload - 项目文件夹打包上传工具

一个用于将本地文件夹打包并上传到远程服务器的Python包。
支持进度回调、.gitignore文件过滤等功能。
"""

from .uploader import ProjectUploader

__version__ = "1.0.0"
__author__ = "pengcunfu"
__email__ = "3173484026@qq.com"

__all__ = ['ProjectUploader']
