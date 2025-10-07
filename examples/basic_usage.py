#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeployUpload 基本使用示例
"""

from deployupload import ProjectUploader


def basic_example():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 创建上传器实例
    uploader = ProjectUploader(
        host='192.168.1.100',
        username='ubuntu',
        password='your_password',
        port=22
    )
    
    # 测试连接
    print("测试服务器连接...")
    if uploader.test_connection():
        print("✅ 服务器连接成功")
        
        # 上传项目文件夹
        try:
            remote_path = uploader.upload_and_extract('.')
            print(f"🎉 项目已上传到: {remote_path}")
        except Exception as e:
            print(f"❌ 上传失败: {e}")
    else:
        print("❌ 服务器连接失败")


def progress_callback_example():
    """带进度回调的示例"""
    print("\n=== 带进度回调的示例 ===")
    
    def my_progress_callback(stage, current, total):
        """自定义进度回调函数"""
        if total > 0:
            percent = (current / total) * 100
            print(f"\r{stage}: {percent:.1f}% ({current}/{total})", end="", flush=True)
        else:
            print(f"\r{stage}: {current}", end="", flush=True)
        
        # 当前阶段完成时换行
        if current == total:
            print()
    
    # 创建上传器
    uploader = ProjectUploader('192.168.1.100', 'ubuntu', 'password')
    
    try:
        # 带进度回调的上传
        remote_path = uploader.upload_and_extract(
            '.',
            progress_callback=my_progress_callback
        )
        print(f"🎉 项目已上传到: {remote_path}")
    except Exception as e:
        print(f"❌ 上传失败: {e}")


def advanced_example():
    """高级配置示例"""
    print("\n=== 高级配置示例 ===")
    
    # 创建上传器
    uploader = ProjectUploader('192.168.1.100', 'ubuntu', 'password')
    
    # 设置额外的忽略模式
    uploader.set_ignore_patterns([
        '*.log',           # 忽略所有日志文件
        'temp/*',          # 忽略temp目录
        '*.tmp',           # 忽略临时文件
        'node_modules/*',  # 忽略node_modules
        '__pycache__/*',   # 忽略Python缓存
    ])
    
    # 设置额外的忽略文件
    uploader.set_ignore_files([
        '/path/to/specific/file.txt',
        '/config/local.yaml',
    ])
    
    # 获取服务器信息
    server_info = uploader.get_server_info()
    print(f"服务器信息: {server_info}")
    
    if server_info['connection_test']:
        print("✅ 服务器连接正常")
        
        try:
            # 只创建压缩包（不上传）
            print("创建压缩包...")
            archive_path = uploader.create_archive('.')
            print(f"✅ 压缩包已创建: {archive_path}")
            
            # 只上传文件（不解压）
            print("上传文件...")
            remote_path = uploader.upload_file(archive_path)
            print(f"✅ 文件已上传到: {remote_path}")
            
            # 清理本地压缩包
            import os
            if os.path.exists(archive_path):
                os.remove(archive_path)
                print(f"✅ 本地压缩包已清理: {archive_path}")
                
        except Exception as e:
            print(f"❌ 操作失败: {e}")
    else:
        print("❌ 服务器连接失败")


def step_by_step_example():
    """分步操作示例"""
    print("\n=== 分步操作示例 ===")
    
    uploader = ProjectUploader('192.168.1.100', 'ubuntu', 'password')
    
    def simple_progress(stage, current, total):
        if total > 0:
            percent = (current / total) * 100
            print(f"{stage}: {percent:.1f}%")
        else:
            print(f"{stage}: 进行中...")
    
    try:
        # 步骤1: 创建压缩包
        print("步骤1: 创建项目压缩包")
        archive_path = uploader.create_archive(
            '.',
            output_path='my_project.tar.gz',
            progress_callback=simple_progress
        )
        print(f"✅ 压缩包创建完成: {archive_path}")
        
        # 步骤2: 上传文件
        print("\n步骤2: 上传文件到服务器")
        remote_archive = uploader.upload_file(
            archive_path,
            '/home/ubuntu/my_project.tar.gz',
            progress_callback=simple_progress
        )
        print(f"✅ 文件上传完成: {remote_archive}")
        
        print("\n🎉 所有步骤完成！")
        
    except Exception as e:
        print(f"❌ 操作失败: {e}")


if __name__ == '__main__':
    # 注意：运行前请修改服务器信息
    print("请先修改示例中的服务器信息（IP、用户名、密码）后再运行")
    print("当前示例使用的是占位符信息，不会实际连接")
    
    # 取消注释下面的行来运行示例
    # basic_example()
    # progress_callback_example()
    # advanced_example()
    # step_by_step_example()
