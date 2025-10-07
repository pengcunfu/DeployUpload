#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI模块的测试用例
"""

import sys
from io import StringIO
from unittest.mock import Mock, patch, call
import pytest

from deployupload.cli import main, get_user_input, progress_callback


class TestProgressCallback:
    """测试进度回调函数"""
    
    def test_progress_callback_with_total(self, capsys):
        """测试有总数的进度回调"""
        progress_callback("测试阶段", 50, 100)
        captured = capsys.readouterr()
        assert "测试阶段: 50.0% (50/100)" in captured.out
    
    def test_progress_callback_without_total(self, capsys):
        """测试无总数的进度回调"""
        progress_callback("测试阶段", 25, 0)
        captured = capsys.readouterr()
        assert "测试阶段: 25" in captured.out
    
    def test_progress_callback_completion(self, capsys):
        """测试完成时的进度回调"""
        progress_callback("测试阶段", 100, 100)
        captured = capsys.readouterr()
        # 应该有换行
        assert captured.out.endswith("\n")


class TestGetUserInput:
    """测试用户输入函数"""
    
    @patch('builtins.input')
    def test_get_user_input_valid(self, mock_input):
        """测试有效的用户输入"""
        mock_input.side_effect = [
            '192.168.1.100',  # host
            'testuser',       # username
            'testpass',       # password
            '22'              # port
        ]
        
        host, username, password, port = get_user_input()
        
        assert host == '192.168.1.100'
        assert username == 'testuser'
        assert password == 'testpass'
        assert port == 22
    
    @patch('builtins.input')
    def test_get_user_input_default_port(self, mock_input):
        """测试默认端口"""
        mock_input.side_effect = [
            '192.168.1.100',  # host
            'testuser',       # username
            'testpass',       # password
            ''                # port (empty, should use default)
        ]
        
        host, username, password, port = get_user_input()
        
        assert port == 22
    
    @patch('builtins.input')
    def test_get_user_input_empty_host(self, mock_input):
        """测试空主机名"""
        mock_input.side_effect = ['']  # empty host
        
        with pytest.raises(SystemExit):
            get_user_input()
    
    @patch('builtins.input')
    def test_get_user_input_empty_username(self, mock_input):
        """测试空用户名"""
        mock_input.side_effect = [
            '192.168.1.100',  # host
            ''                # empty username
        ]
        
        with pytest.raises(SystemExit):
            get_user_input()
    
    @patch('builtins.input')
    def test_get_user_input_empty_password(self, mock_input):
        """测试空密码"""
        mock_input.side_effect = [
            '192.168.1.100',  # host
            'testuser',       # username
            ''                # empty password
        ]
        
        with pytest.raises(SystemExit):
            get_user_input()
    
    @patch('builtins.input')
    def test_get_user_input_invalid_port(self, mock_input):
        """测试无效端口"""
        mock_input.side_effect = [
            '192.168.1.100',  # host
            'testuser',       # username
            'testpass',       # password
            'invalid_port'    # invalid port
        ]
        
        with pytest.raises(SystemExit):
            get_user_input()


class TestMainFunction:
    """测试主函数"""
    
    @patch('deployupload.cli.ProjectUploader')
    @patch('sys.argv', ['deployupload', '--host', '192.168.1.100', '--username', 'test', '--password', 'pass'])
    def test_main_with_args(self, mock_uploader_class):
        """测试带参数的主函数"""
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader
        mock_uploader.test_connection.return_value = True
        mock_uploader.upload_and_extract.return_value = '/home/test/project'
        
        # 模拟成功执行
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_not_called()
        
        # 验证上传器被正确创建和调用
        mock_uploader_class.assert_called_once_with('192.168.1.100', 'test', 'pass', 22)
        mock_uploader.test_connection.assert_called_once()
        mock_uploader.upload_and_extract.assert_called_once()
    
    @patch('deployupload.cli.get_user_input')
    @patch('deployupload.cli.ProjectUploader')
    @patch('sys.argv', ['deployupload', '--interactive'])
    def test_main_interactive_mode(self, mock_uploader_class, mock_get_input):
        """测试交互模式"""
        mock_get_input.return_value = ('192.168.1.100', 'test', 'pass', 22)
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader
        mock_uploader.test_connection.return_value = True
        mock_uploader.upload_and_extract.return_value = '/home/test/project'
        
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_not_called()
        
        mock_get_input.assert_called_once()
        mock_uploader_class.assert_called_once_with('192.168.1.100', 'test', 'pass', 22)
    
    @patch('deployupload.cli.ProjectUploader')
    @patch('sys.argv', ['deployupload', '--host', '192.168.1.100', '--username', 'test', '--password', 'pass'])
    def test_main_connection_failure(self, mock_uploader_class):
        """测试连接失败"""
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader
        mock_uploader.test_connection.return_value = False
        
        with pytest.raises(SystemExit):
            main()
        
        mock_uploader.test_connection.assert_called_once()
        # 不应该调用上传方法
        mock_uploader.upload_and_extract.assert_not_called()
    
    @patch('deployupload.cli.ProjectUploader')
    @patch('sys.argv', ['deployupload', '--host', '192.168.1.100', '--username', 'test', '--password', 'pass'])
    def test_main_upload_failure(self, mock_uploader_class):
        """测试上传失败"""
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader
        mock_uploader.test_connection.return_value = True
        mock_uploader.upload_and_extract.side_effect = Exception('Upload failed')
        
        with pytest.raises(SystemExit):
            main()
        
        mock_uploader.upload_and_extract.assert_called_once()
    
    @patch('sys.argv', ['deployupload', '--host', '192.168.1.100', '--username', 'test', '--password', 'pass', '--project-root', '/nonexistent'])
    def test_main_nonexistent_project_root(self):
        """测试不存在的项目根目录"""
        with pytest.raises(SystemExit):
            main()
    
    @patch('deployupload.cli.ProjectUploader')
    @patch('sys.argv', ['deployupload', '--host', '192.168.1.100', '--username', 'test', '--password', 'pass', '--remote-dir', '/opt/projects'])
    def test_main_with_custom_remote_dir(self, mock_uploader_class):
        """测试自定义远程目录"""
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader
        mock_uploader.test_connection.return_value = True
        mock_uploader.upload_and_extract.return_value = '/opt/projects/project'
        
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_not_called()
        
        # 验证传递了正确的远程目录
        args, kwargs = mock_uploader.upload_and_extract.call_args
        assert '/opt/projects' in args or '/opt/projects' in kwargs.values()
    
    @patch('sys.argv', ['deployupload'])
    def test_main_missing_dependencies(self):
        """测试缺少依赖"""
        with patch('builtins.__import__', side_effect=ImportError('No module named paramiko')):
            with pytest.raises(SystemExit):
                main()
    
    @patch('deployupload.cli.ProjectUploader')
    @patch('sys.argv', ['deployupload', '--host', '192.168.1.100', '--username', 'test', '--password', 'pass'])
    def test_main_keyboard_interrupt(self, mock_uploader_class):
        """测试键盘中断"""
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader
        mock_uploader.test_connection.return_value = True
        mock_uploader.upload_and_extract.side_effect = KeyboardInterrupt()
        
        with pytest.raises(SystemExit):
            main()


class TestArgumentParsing:
    """测试参数解析"""
    
    @patch('deployupload.cli.ProjectUploader')
    @patch('sys.argv', ['deployupload', '--help'])
    def test_help_argument(self, mock_uploader_class):
        """测试帮助参数"""
        with pytest.raises(SystemExit) as exc_info:
            main()
        # argparse的help会以状态码0退出
        assert exc_info.value.code == 0
    
    @patch('deployupload.cli.ProjectUploader')
    @patch('sys.argv', ['deployupload', '--host', '192.168.1.100', '--username', 'test', '--password', 'pass', '--port', '2222'])
    def test_custom_port_argument(self, mock_uploader_class):
        """测试自定义端口参数"""
        mock_uploader = Mock()
        mock_uploader_class.return_value = mock_uploader
        mock_uploader.test_connection.return_value = True
        mock_uploader.upload_and_extract.return_value = '/home/test/project'
        
        with patch('sys.exit') as mock_exit:
            main()
            mock_exit.assert_not_called()
        
        # 验证使用了自定义端口
        mock_uploader_class.assert_called_once_with('192.168.1.100', 'test', 'pass', 2222)
