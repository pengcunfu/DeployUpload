#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest配置文件和共享fixtures
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest
from unittest.mock import Mock, patch
import paramiko

from deployupload import ProjectUploader


@pytest.fixture
def temp_project_dir():
    """创建临时测试项目目录"""
    temp_dir = Path(tempfile.mkdtemp(prefix='test_project_'))
    
    # 创建测试文件结构
    (temp_dir / 'main.py').write_text('''#!/usr/bin/env python3
print("Hello, World!")
''')
    
    (temp_dir / 'README.md').write_text('''# Test Project
This is a test project for DeployUpload.
''')
    
    (temp_dir / 'requirements.txt').write_text('''requests>=2.25.0
flask>=2.0.0
''')
    
    # 创建子目录
    src_dir = temp_dir / 'src'
    src_dir.mkdir()
    (src_dir / 'utils.py').write_text('''def hello():
    return "Hello from utils!"
''')
    
    (src_dir / '__init__.py').write_text('')
    
    # 创建应该被忽略的文件
    (temp_dir / 'debug.log').write_text('Debug log content')
    (temp_dir / 'cache.tmp').write_text('Temporary cache')
    
    # 创建临时目录
    temp_subdir = temp_dir / 'temp'
    temp_subdir.mkdir()
    (temp_subdir / 'temp_file.txt').write_text('Temporary file')
    
    # 创建.gitignore文件
    (temp_dir / '.gitignore').write_text('''*.log
*.tmp
temp/
__pycache__/
.env
node_modules/
''')
    
    # 创建.deploy_ignore文件
    (temp_dir / '.deploy_ignore').write_text('''*.bak
backup/
local_config.yaml
''')
    
    yield temp_dir
    
    # 清理
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_uploader():
    """创建模拟的上传器实例"""
    return ProjectUploader('test.example.com', 'testuser', 'testpass', 22)


@pytest.fixture
def mock_ssh_client():
    """模拟SSH客户端"""
    with patch('paramiko.SSHClient') as mock_ssh:
        mock_instance = Mock()
        mock_ssh.return_value = mock_instance
        
        # 模拟连接成功
        mock_instance.connect.return_value = None
        mock_instance.close.return_value = None
        
        # 模拟命令执行
        mock_stdout = Mock()
        mock_stderr = Mock()
        mock_stdin = Mock()
        
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stderr.read.return_value = b''
        
        mock_instance.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        yield mock_instance


@pytest.fixture
def mock_sftp_client():
    """模拟SFTP客户端"""
    with patch('paramiko.SSHClient.open_sftp') as mock_sftp:
        mock_instance = Mock()
        mock_sftp.return_value = mock_instance
        
        # 模拟上传成功
        mock_instance.put.return_value = None
        mock_instance.close.return_value = None
        
        yield mock_instance


@pytest.fixture
def progress_tracker():
    """进度跟踪器fixture"""
    class ProgressTracker:
        def __init__(self):
            self.calls = []
        
        def __call__(self, stage, current, total):
            self.calls.append({
                'stage': stage,
                'current': current,
                'total': total
            })
        
        def get_stages(self):
            return [call['stage'] for call in self.calls]
        
        def get_final_progress(self, stage):
            stage_calls = [call for call in self.calls if call['stage'] == stage]
            if stage_calls:
                return stage_calls[-1]
            return None
    
    return ProgressTracker()


@pytest.fixture(autouse=True)
def clean_temp_files():
    """自动清理测试产生的临时文件"""
    yield
    
    # 清理当前目录下的测试文件
    test_files = [
        'test_project.tar.gz',
        'TestProject.tar.gz',
        'temp_project.tar.gz'
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
