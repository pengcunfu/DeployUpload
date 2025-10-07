#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProjectUploader类的测试用例
"""

import os
import tempfile
import tarfile
from pathlib import Path
from unittest.mock import Mock, patch, call
import pytest
import paramiko

from deployupload import ProjectUploader


class TestProjectUploaderInit:
    """测试ProjectUploader初始化"""
    
    def test_init_with_default_port(self):
        """测试默认端口初始化"""
        uploader = ProjectUploader('test.com', 'user', 'pass')
        assert uploader.host == 'test.com'
        assert uploader.username == 'user'
        assert uploader.password == 'pass'
        assert uploader.port == 22
    
    def test_init_with_custom_port(self):
        """测试自定义端口初始化"""
        uploader = ProjectUploader('test.com', 'user', 'pass', 2222)
        assert uploader.port == 2222
    
    def test_init_internal_state(self):
        """测试内部状态初始化"""
        uploader = ProjectUploader('test.com', 'user', 'pass')
        assert isinstance(uploader._ignored_patterns, set)
        assert isinstance(uploader._ignored_files, set)
        assert len(uploader._ignored_patterns) == 0
        assert len(uploader._ignored_files) == 0


class TestIgnorePatterns:
    """测试忽略模式功能"""
    
    def test_set_ignore_patterns(self, mock_uploader):
        """测试设置忽略模式"""
        patterns = ['*.log', '*.tmp', 'temp/*']
        mock_uploader.set_ignore_patterns(patterns)
        
        assert '*.log' in mock_uploader._ignored_patterns
        assert '*.tmp' in mock_uploader._ignored_patterns
        assert 'temp/*' in mock_uploader._ignored_patterns
    
    def test_set_ignore_files(self, mock_uploader):
        """测试设置忽略文件"""
        files = ['/path/to/file1.txt', '/path/to/file2.txt']
        mock_uploader.set_ignore_files(files)
        
        assert '/path/to/file1.txt' in mock_uploader._ignored_files
        assert '/path/to/file2.txt' in mock_uploader._ignored_files
    
    def test_should_ignore_system_files(self, mock_uploader, temp_project_dir):
        """测试系统文件忽略"""
        # 创建系统文件
        system_files = ['.DS_Store', 'Thumbs.db', '__pycache__']
        
        for filename in system_files:
            file_path = temp_project_dir / filename
            if filename == '__pycache__':
                file_path.mkdir()
            else:
                file_path.touch()
            
            assert mock_uploader._should_ignore_file(file_path) == True
    
    def test_gitignore_parsing(self, mock_uploader, temp_project_dir):
        """测试.gitignore文件解析"""
        mock_uploader._collect_gitignore_patterns(temp_project_dir)
        
        # 检查是否正确解析了.gitignore中的模式
        patterns_str = str(mock_uploader._ignored_patterns)
        assert '*.log' in patterns_str or 'debug.log' in patterns_str
        assert '*.tmp' in patterns_str or 'cache.tmp' in patterns_str


class TestArchiveCreation:
    """测试压缩包创建功能"""
    
    def test_create_archive_basic(self, mock_uploader, temp_project_dir):
        """测试基本压缩包创建"""
        archive_path = mock_uploader.create_archive(str(temp_project_dir))
        
        assert os.path.exists(archive_path)
        assert archive_path.endswith('.tar.gz')
        
        # 验证压缩包内容
        with tarfile.open(archive_path, 'r:gz') as tar:
            names = tar.getnames()
            # 应该包含主要文件
            assert any('main.py' in name for name in names)
            assert any('README.md' in name for name in names)
            # 不应该包含被忽略的文件
            assert not any('debug.log' in name for name in names)
            assert not any('cache.tmp' in name for name in names)
        
        # 清理
        os.remove(archive_path)
    
    def test_create_archive_with_custom_output(self, mock_uploader, temp_project_dir):
        """测试自定义输出路径"""
        custom_path = 'custom_archive.tar.gz'
        archive_path = mock_uploader.create_archive(
            str(temp_project_dir), 
            output_path=custom_path
        )
        
        assert archive_path == custom_path
        assert os.path.exists(custom_path)
        
        # 清理
        os.remove(custom_path)
    
    def test_create_archive_with_progress_callback(self, mock_uploader, temp_project_dir, progress_tracker):
        """测试带进度回调的压缩包创建"""
        archive_path = mock_uploader.create_archive(
            str(temp_project_dir),
            progress_callback=progress_tracker
        )
        
        assert os.path.exists(archive_path)
        
        # 验证进度回调被调用
        stages = progress_tracker.get_stages()
        assert '收集忽略模式' in stages
        assert '计算文件数量' in stages
        assert '复制文件' in stages
        assert '创建压缩包' in stages
        
        # 清理
        os.remove(archive_path)
    
    def test_create_archive_nonexistent_directory(self, mock_uploader):
        """测试不存在的目录"""
        with pytest.raises(Exception):
            mock_uploader.create_archive('/nonexistent/directory')


class TestConnectionMethods:
    """测试连接相关方法"""
    
    @patch('paramiko.SSHClient')
    def test_test_connection_success(self, mock_ssh_class, mock_uploader):
        """测试连接成功"""
        mock_ssh = Mock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.connect.return_value = None
        mock_ssh.close.return_value = None
        
        result = mock_uploader.test_connection()
        
        assert result == True
        mock_ssh.connect.assert_called_once_with(
            'test.example.com', 22, 'testuser', 'testpass', timeout=10
        )
        mock_ssh.close.assert_called_once()
    
    @patch('paramiko.SSHClient')
    def test_test_connection_failure(self, mock_ssh_class, mock_uploader):
        """测试连接失败"""
        mock_ssh = Mock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.connect.side_effect = paramiko.AuthenticationException()
        
        result = mock_uploader.test_connection()
        
        assert result == False
    
    def test_get_server_info(self, mock_uploader):
        """测试获取服务器信息"""
        with patch.object(mock_uploader, 'test_connection', return_value=True):
            info = mock_uploader.get_server_info()
            
            assert info['host'] == 'test.example.com'
            assert info['username'] == 'testuser'
            assert info['port'] == 22
            assert info['connection_test'] == True


class TestFileUpload:
    """测试文件上传功能"""
    
    @patch('paramiko.SSHClient')
    def test_upload_file_success(self, mock_ssh_class, mock_uploader, temp_project_dir):
        """测试文件上传成功"""
        # 创建测试文件
        test_file = temp_project_dir / 'test_upload.txt'
        test_file.write_text('Test content')
        
        # 设置mock
        mock_ssh = Mock()
        mock_sftp = Mock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.open_sftp.return_value = mock_sftp
        
        # 执行上传
        result = mock_uploader.upload_file(str(test_file))
        
        # 验证结果
        assert result == f'/home/testuser/{test_file.name}'
        mock_ssh.connect.assert_called_once()
        mock_sftp.put.assert_called_once()
        mock_sftp.close.assert_called_once()
        mock_ssh.close.assert_called_once()
    
    def test_upload_file_nonexistent(self, mock_uploader):
        """测试上传不存在的文件"""
        with pytest.raises(FileNotFoundError):
            mock_uploader.upload_file('/nonexistent/file.txt')
    
    @patch('paramiko.SSHClient')
    def test_upload_file_with_progress(self, mock_ssh_class, mock_uploader, temp_project_dir, progress_tracker):
        """测试带进度回调的文件上传"""
        # 创建测试文件
        test_file = temp_project_dir / 'test_upload.txt'
        test_file.write_text('Test content for progress tracking')
        
        # 设置mock
        mock_ssh = Mock()
        mock_sftp = Mock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.open_sftp.return_value = mock_sftp
        
        # 执行上传
        mock_uploader.upload_file(str(test_file), progress_callback=progress_tracker)
        
        # 验证进度回调
        stages = progress_tracker.get_stages()
        assert '连接服务器' in stages
        assert '上传文件' in stages


class TestUploadAndExtract:
    """测试完整的上传和解压功能"""
    
    @patch('paramiko.SSHClient')
    def test_upload_and_extract_success(self, mock_ssh_class, mock_uploader, temp_project_dir):
        """测试完整上传和解压成功"""
        # 设置mock
        mock_ssh = Mock()
        mock_sftp = Mock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.open_sftp.return_value = mock_sftp
        
        # 模拟命令执行成功
        mock_stdout = Mock()
        mock_stderr = Mock()
        mock_stdin = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stderr.read.return_value = b''
        mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # 执行上传和解压
        result = mock_uploader.upload_and_extract(str(temp_project_dir))
        
        # 验证结果
        project_name = temp_project_dir.name
        expected_path = f'/home/testuser/{project_name}'
        assert result == expected_path
        
        # 验证SSH连接被调用两次（上传和解压）
        assert mock_ssh.connect.call_count == 2
        mock_sftp.put.assert_called_once()
        mock_ssh.exec_command.assert_called_once()
    
    @patch('paramiko.SSHClient')
    def test_upload_and_extract_with_custom_remote_dir(self, mock_ssh_class, mock_uploader, temp_project_dir):
        """测试自定义远程目录"""
        # 设置mock
        mock_ssh = Mock()
        mock_sftp = Mock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.open_sftp.return_value = mock_sftp
        
        # 模拟命令执行成功
        mock_stdout = Mock()
        mock_stderr = Mock()
        mock_stdin = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        mock_stderr.read.return_value = b''
        mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # 执行上传和解压
        custom_dir = '/opt/projects'
        result = mock_uploader.upload_and_extract(
            str(temp_project_dir), 
            remote_dir=custom_dir
        )
        
        # 验证结果
        project_name = temp_project_dir.name
        expected_path = f'{custom_dir}/{project_name}'
        assert result == expected_path
    
    @patch('paramiko.SSHClient')
    def test_upload_and_extract_extract_failure(self, mock_ssh_class, mock_uploader, temp_project_dir):
        """测试解压失败"""
        # 设置mock
        mock_ssh = Mock()
        mock_sftp = Mock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.open_sftp.return_value = mock_sftp
        
        # 模拟解压命令失败
        mock_stdout = Mock()
        mock_stderr = Mock()
        mock_stdin = Mock()
        mock_stdout.channel.recv_exit_status.return_value = 1  # 失败
        mock_stderr.read.return_value = b'Extract failed'
        mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # 执行上传和解压，应该抛出异常
        with pytest.raises(Exception, match='解压失败'):
            mock_uploader.upload_and_extract(str(temp_project_dir))


class TestErrorHandling:
    """测试错误处理"""
    
    @patch('paramiko.SSHClient')
    def test_connection_timeout(self, mock_ssh_class, mock_uploader):
        """测试连接超时"""
        mock_ssh = Mock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.connect.side_effect = TimeoutError('Connection timeout')
        
        with pytest.raises(Exception, match='上传失败'):
            mock_uploader.upload_file('test.txt')
    
    @patch('paramiko.SSHClient')
    def test_authentication_failure(self, mock_ssh_class, mock_uploader):
        """测试认证失败"""
        mock_ssh = Mock()
        mock_ssh_class.return_value = mock_ssh
        mock_ssh.connect.side_effect = paramiko.AuthenticationException('Auth failed')
        
        with pytest.raises(Exception, match='上传失败'):
            mock_uploader.upload_file('test.txt')


class TestIntegration:
    """集成测试"""
    
    def test_full_workflow_dry_run(self, temp_project_dir):
        """测试完整工作流程（不实际连接服务器）"""
        uploader = ProjectUploader('test.example.com', 'testuser', 'testpass')
        
        # 设置忽略模式
        uploader.set_ignore_patterns(['*.log', '*.tmp'])
        
        # 创建压缩包
        archive_path = uploader.create_archive(str(temp_project_dir))
        
        # 验证压缩包
        assert os.path.exists(archive_path)
        
        # 验证压缩包内容
        with tarfile.open(archive_path, 'r:gz') as tar:
            names = tar.getnames()
            # 应该包含主要文件
            assert any('main.py' in name for name in names)
            assert any('README.md' in name for name in names)
            # 不应该包含被忽略的文件
            assert not any('debug.log' in name for name in names)
            assert not any('cache.tmp' in name for name in names)
        
        # 清理
        os.remove(archive_path)
