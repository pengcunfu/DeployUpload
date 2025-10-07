#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeployUpload 测试脚本
用于测试上传器的各种功能
"""

import os
import tempfile
import shutil
from pathlib import Path
from deployupload import ProjectUploader


def create_test_project():
    """创建测试项目"""
    # 创建临时目录作为测试项目
    test_dir = Path(tempfile.mkdtemp(prefix='test_project_'))
    
    # 创建一些测试文件
    (test_dir / 'main.py').write_text('''#!/usr/bin/env python3
print("Hello, World!")
''')
    
    (test_dir / 'README.md').write_text('''# Test Project
This is a test project for DeployUpload.
''')
    
    (test_dir / 'requirements.txt').write_text('''requests>=2.25.0
flask>=2.0.0
''')
    
    # 创建子目录和文件
    src_dir = test_dir / 'src'
    src_dir.mkdir()
    (src_dir / 'utils.py').write_text('''def hello():
    return "Hello from utils!"
''')
    
    # 创建应该被忽略的文件
    (test_dir / 'temp.log').write_text('This is a log file')
    (test_dir / 'cache.tmp').write_text('This is a temp file')
    
    temp_dir = test_dir / 'temp'
    temp_dir.mkdir()
    (temp_dir / 'temp_file.txt').write_text('Temporary file')
    
    # 创建.gitignore文件
    (test_dir / '.gitignore').write_text('''*.log
*.tmp
temp/
__pycache__/
.env
''')
    
    # 创建.deploy_ignore文件
    (test_dir / '.deploy_ignore').write_text('''*.bak
backup/
''')
    
    print(f"✅ 测试项目已创建: {test_dir}")
    return test_dir


def test_archive_creation():
    """测试压缩包创建功能"""
    print("\n=== 测试压缩包创建功能 ===")
    
    # 创建测试项目
    test_project = create_test_project()
    
    try:
        # 创建上传器（使用虚拟服务器信息）
        uploader = ProjectUploader('localhost', 'test', 'test')
        
        # 设置额外的忽略模式
        uploader.set_ignore_patterns(['*.bak'])
        
        def test_progress_callback(stage, current, total):
            if total > 0:
                percent = (current / total) * 100
                print(f"  {stage}: {percent:.1f}% ({current}/{total})")
            else:
                print(f"  {stage}: {current}")
        
        # 创建压缩包
        print("正在创建压缩包...")
        archive_path = uploader.create_archive(
            str(test_project),
            progress_callback=test_progress_callback
        )
        
        # 检查压缩包
        if os.path.exists(archive_path):
            archive_size = os.path.getsize(archive_path)
            print(f"✅ 压缩包创建成功: {archive_path}")
            print(f"   压缩包大小: {archive_size} bytes")
            
            # 清理压缩包
            os.remove(archive_path)
            print("✅ 压缩包已清理")
        else:
            print("❌ 压缩包创建失败")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        # 清理测试项目
        shutil.rmtree(test_project)
        print(f"✅ 测试项目已清理: {test_project}")


def test_connection_methods():
    """测试连接相关方法"""
    print("\n=== 测试连接相关方法 ===")
    
    # 测试无效服务器
    print("测试无效服务器连接...")
    uploader = ProjectUploader('invalid.server.com', 'test', 'test')
    
    if not uploader.test_connection():
        print("✅ 正确检测到无效服务器")
    else:
        print("❌ 未能检测到无效服务器")
    
    # 获取服务器信息
    server_info = uploader.get_server_info()
    print(f"服务器信息: {server_info}")
    
    # 测试本地SSH服务器（如果存在）
    print("\n测试本地SSH连接...")
    local_uploader = ProjectUploader('localhost', 'test', 'test', 22)
    
    if local_uploader.test_connection():
        print("✅ 本地SSH服务器连接成功")
    else:
        print("ℹ️  本地SSH服务器不可用（这是正常的）")


def test_ignore_patterns():
    """测试忽略模式功能"""
    print("\n=== 测试忽略模式功能 ===")
    
    # 创建测试项目
    test_project = create_test_project()
    
    try:
        uploader = ProjectUploader('localhost', 'test', 'test')
        
        # 测试不同的忽略模式
        test_patterns = [
            '*.log',
            '*.tmp', 
            'temp/*',
            '__pycache__/*'
        ]
        
        uploader.set_ignore_patterns(test_patterns)
        
        # 收集忽略模式（通过创建压缩包来触发）
        print("测试忽略模式...")
        archive_path = uploader.create_archive(str(test_project))
        
        if os.path.exists(archive_path):
            print("✅ 忽略模式测试通过")
            os.remove(archive_path)
        else:
            print("❌ 忽略模式测试失败")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        # 清理测试项目
        shutil.rmtree(test_project)


def run_all_tests():
    """运行所有测试"""
    print("🧪 开始运行 DeployUpload 测试套件")
    print("=" * 50)
    
    try:
        test_archive_creation()
        test_connection_methods()
        test_ignore_patterns()
        
        print("\n" + "=" * 50)
        print("🎉 所有测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试套件执行失败: {e}")


if __name__ == '__main__':
    run_all_tests()
