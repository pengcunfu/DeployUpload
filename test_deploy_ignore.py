#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试.deploy_ignore文件功能
"""

import tempfile
import shutil
from pathlib import Path
from deployupload import ProjectUploader

def test_deploy_ignore():
    """测试.deploy_ignore文件是否正常工作"""
    # 创建临时测试目录
    temp_dir = Path(tempfile.mkdtemp(prefix='test_deploy_ignore_'))
    
    try:
        # 创建测试文件
        (temp_dir / 'main.py').write_text('print("Hello")')
        (temp_dir / 'README.md').write_text('# Test Project')
        (temp_dir / 'tests').mkdir()
        (temp_dir / 'tests' / 'test_main.py').write_text('def test_main(): pass')
        (temp_dir / 'docs').mkdir()
        (temp_dir / 'docs' / 'guide.md').write_text('# Guide')
        
        # 创建.deploy_ignore文件
        (temp_dir / '.deploy_ignore').write_text('''# 测试忽略规则
tests/
docs/
README.md
''')
        
        # 创建上传器并测试
        uploader = ProjectUploader('test.com', 'user', 'pass')
        
        # 创建压缩包
        archive_path = uploader.create_archive(str(temp_dir))
        
        print(f"✅ 压缩包创建成功: {archive_path}")
        
        # 检查压缩包内容
        import tarfile
        with tarfile.open(archive_path, 'r:gz') as tar:
            names = tar.getnames()
            print("压缩包内容:")
            for name in sorted(names):
                print(f"  {name}")
            
            # 验证忽略规则是否生效
            should_include = any('main.py' in name for name in names)
            should_exclude_tests = not any('test_main.py' in name for name in names)
            should_exclude_docs = not any('guide.md' in name for name in names)
            should_exclude_readme = not any('README.md' in name for name in names)
            
            if should_include and should_exclude_tests and should_exclude_docs and should_exclude_readme:
                print("✅ .deploy_ignore 文件工作正常！")
                print("  - main.py 被包含 ✓")
                print("  - tests/ 被忽略 ✓")
                print("  - docs/ 被忽略 ✓")
                print("  - README.md 被忽略 ✓")
            else:
                print("❌ .deploy_ignore 文件未正常工作")
                print(f"  - main.py 被包含: {should_include}")
                print(f"  - tests/ 被忽略: {should_exclude_tests}")
                print(f"  - docs/ 被忽略: {should_exclude_docs}")
                print(f"  - README.md 被忽略: {should_exclude_readme}")
        
        # 清理压缩包
        Path(archive_path).unlink()
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    test_deploy_ignore()
