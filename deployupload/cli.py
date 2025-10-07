#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeployUpload 命令行接口
"""

import argparse
import sys
from pathlib import Path
from .uploader import ProjectUploader


def progress_callback(stage: str, current: int, total: int):
    """简单的进度回调函数"""
    if total > 0:
        percent = (current / total) * 100
        print(f"\r{stage}: {percent:.1f}% ({current}/{total})", end="", flush=True)
    else:
        print(f"\r{stage}: {current}", end="", flush=True)
    
    if current == total:
        print()  # 换行


def get_user_input():
    """获取用户输入的服务器信息"""
    print("=== DeployUpload 项目上传工具 ===\n")
    
    host = input("请输入服务器IP地址: ").strip()
    if not host:
        print("错误: 服务器IP地址不能为空")
        sys.exit(1)
    
    username = input("请输入服务器用户名: ").strip()
    if not username:
        print("错误: 用户名不能为空")
        sys.exit(1)
    
    password = input("请输入服务器密码: ").strip()
    if not password:
        print("错误: 密码不能为空")
        sys.exit(1)
    
    port = input("请输入SSH端口 (默认22): ").strip()
    if not port:
        port = 22
    else:
        try:
            port = int(port)
        except ValueError:
            print("错误: 端口必须是数字")
            sys.exit(1)
    
    return host, username, password, port


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='DeployUpload - 项目文件夹打包上传工具')
    parser.add_argument('--host', help='服务器IP地址')
    parser.add_argument('--username', help='服务器用户名')
    parser.add_argument('--password', help='服务器密码')
    parser.add_argument('--port', type=int, default=22, help='SSH端口 (默认: 22)')
    parser.add_argument('--project-root', default='.', help='项目根目录 (默认: 当前目录)')
    parser.add_argument('--remote-dir', help='远程目录 (默认: 用户home目录)')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式输入服务器信息')
    
    args = parser.parse_args()
    
    # 检查依赖
    try:
        import paramiko
        import tqdm
    except ImportError as e:
        print(f"缺少必要的依赖包: {e}")
        print("请安装: pip install deployupload")
        sys.exit(1)
    
    # 获取服务器信息
    if args.interactive or not all([args.host, args.username, args.password]):
        host, username, password, port = get_user_input()
    else:
        host, username, password, port = args.host, args.username, args.password, args.port
    
    # 获取项目根目录
    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        print(f"错误: 项目目录不存在: {project_root}")
        sys.exit(1)
    
    print(f"项目根目录: {project_root}")
    
    try:
        # 创建上传器
        uploader = ProjectUploader(host, username, password, port)
        
        # 测试连接
        print("正在测试服务器连接...")
        if not uploader.test_connection():
            print("❌ 服务器连接失败，请检查服务器信息")
            sys.exit(1)
        print("✅ 服务器连接成功")
        
        # 上传项目
        print("开始上传项目...")
        remote_project_path = uploader.upload_and_extract(
            str(project_root),
            args.remote_dir,
            progress_callback=progress_callback
        )
        
        print(f"\n🎉 项目上传完成！")
        print(f"远程项目路径: {remote_project_path}")
        
    except KeyboardInterrupt:
        print("\n❌ 操作被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 操作失败: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
