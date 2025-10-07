#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeployUpload 高级使用示例
包含错误处理、日志记录、配置管理等
"""

import os
import json
import logging
from pathlib import Path
from deployupload import ProjectUploader


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeployConfig:
    """部署配置管理类"""
    
    def __init__(self, config_file='deploy_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            default_config = {
                "servers": {
                    "development": {
                        "host": "192.168.1.100",
                        "username": "dev",
                        "password": "dev_password",
                        "port": 22,
                        "remote_dir": "/home/dev/projects"
                    },
                    "staging": {
                        "host": "192.168.1.101",
                        "username": "staging",
                        "password": "staging_password",
                        "port": 22,
                        "remote_dir": "/home/staging/projects"
                    },
                    "production": {
                        "host": "192.168.1.102",
                        "username": "prod",
                        "password": "prod_password",
                        "port": 22,
                        "remote_dir": "/home/prod/projects"
                    }
                },
                "ignore_patterns": [
                    "*.log",
                    "*.tmp",
                    "temp/*",
                    "cache/*",
                    "node_modules/*",
                    "__pycache__/*",
                    ".pytest_cache/*",
                    "*.pyc",
                    ".env",
                    ".venv/*"
                ],
                "ignore_files": [
                    "config/local.yaml",
                    "config/development.yaml"
                ]
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """保存配置文件"""
        if config is None:
            config = self.config
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def get_server_config(self, env):
        """获取指定环境的服务器配置"""
        return self.config.get('servers', {}).get(env)
    
    def get_ignore_patterns(self):
        """获取忽略模式"""
        return self.config.get('ignore_patterns', [])
    
    def get_ignore_files(self):
        """获取忽略文件"""
        return self.config.get('ignore_files', [])


class AdvancedUploader:
    """高级上传器，包含错误处理和日志记录"""
    
    def __init__(self, config_file='deploy_config.json'):
        self.config = DeployConfig(config_file)
        self.uploader = None
        self.current_env = None
    
    def setup_uploader(self, env):
        """设置上传器"""
        server_config = self.config.get_server_config(env)
        if not server_config:
            raise ValueError(f"未找到环境 '{env}' 的配置")
        
        self.uploader = ProjectUploader(
            host=server_config['host'],
            username=server_config['username'],
            password=server_config['password'],
            port=server_config.get('port', 22)
        )
        
        # 设置忽略模式
        self.uploader.set_ignore_patterns(self.config.get_ignore_patterns())
        self.uploader.set_ignore_files(self.config.get_ignore_files())
        
        self.current_env = env
        logger.info(f"已设置上传器，目标环境: {env}")
    
    def progress_callback(self, stage, current, total):
        """进度回调函数"""
        if total > 0:
            percent = (current / total) * 100
            logger.info(f"{stage}: {percent:.1f}% ({current}/{total})")
        else:
            logger.info(f"{stage}: {current}")
    
    def test_connection(self):
        """测试连接"""
        if not self.uploader:
            raise ValueError("请先调用 setup_uploader() 设置上传器")
        
        logger.info("正在测试服务器连接...")
        if self.uploader.test_connection():
            logger.info("✅ 服务器连接成功")
            return True
        else:
            logger.error("❌ 服务器连接失败")
            return False
    
    def deploy_project(self, project_root='.', dry_run=False):
        """部署项目"""
        if not self.uploader:
            raise ValueError("请先调用 setup_uploader() 设置上传器")
        
        project_root = Path(project_root).resolve()
        logger.info(f"开始部署项目: {project_root}")
        logger.info(f"目标环境: {self.current_env}")
        
        if dry_run:
            logger.info("🔍 DRY RUN 模式 - 仅创建压缩包，不上传")
            try:
                archive_path = self.uploader.create_archive(
                    str(project_root),
                    progress_callback=self.progress_callback
                )
                logger.info(f"✅ 压缩包创建成功: {archive_path}")
                
                # 显示压缩包信息
                archive_size = os.path.getsize(archive_path)
                logger.info(f"压缩包大小: {archive_size / 1024 / 1024:.2f} MB")
                
                # 清理压缩包
                os.remove(archive_path)
                logger.info("✅ DRY RUN 完成，压缩包已清理")
                
            except Exception as e:
                logger.error(f"❌ DRY RUN 失败: {e}")
                raise
        else:
            # 实际部署
            if not self.test_connection():
                raise Exception("服务器连接失败，无法继续部署")
            
            try:
                server_config = self.config.get_server_config(self.current_env)
                remote_dir = server_config.get('remote_dir', f'/home/{server_config["username"]}')
                
                remote_path = self.uploader.upload_and_extract(
                    str(project_root),
                    remote_dir=remote_dir,
                    progress_callback=self.progress_callback
                )
                
                logger.info(f"🎉 项目部署成功！")
                logger.info(f"远程路径: {remote_path}")
                return remote_path
                
            except Exception as e:
                logger.error(f"❌ 部署失败: {e}")
                raise
    
    def batch_deploy(self, environments, project_root='.'):
        """批量部署到多个环境"""
        results = {}
        
        for env in environments:
            logger.info(f"\n{'='*50}")
            logger.info(f"开始部署到环境: {env}")
            logger.info(f"{'='*50}")
            
            try:
                self.setup_uploader(env)
                remote_path = self.deploy_project(project_root)
                results[env] = {'status': 'success', 'path': remote_path}
                logger.info(f"✅ 环境 {env} 部署成功")
                
            except Exception as e:
                results[env] = {'status': 'failed', 'error': str(e)}
                logger.error(f"❌ 环境 {env} 部署失败: {e}")
        
        # 输出总结
        logger.info(f"\n{'='*50}")
        logger.info("批量部署总结:")
        logger.info(f"{'='*50}")
        
        for env, result in results.items():
            if result['status'] == 'success':
                logger.info(f"✅ {env}: 成功 - {result['path']}")
            else:
                logger.error(f"❌ {env}: 失败 - {result['error']}")
        
        return results


def main():
    """主函数示例"""
    # 创建高级上传器
    uploader = AdvancedUploader()
    
    try:
        # 示例1: 部署到开发环境
        print("示例1: 部署到开发环境")
        uploader.setup_uploader('development')
        
        # 先进行 dry run 测试
        print("进行 DRY RUN 测试...")
        uploader.deploy_project(dry_run=True)
        
        # 实际部署（注释掉以避免实际执行）
        # uploader.deploy_project()
        
        # 示例2: 批量部署
        print("\n示例2: 批量部署")
        environments = ['development', 'staging']  # 'production'
        # results = uploader.batch_deploy(environments)
        
        print("\n✅ 所有示例完成")
        
    except Exception as e:
        logger.error(f"❌ 示例执行失败: {e}")


if __name__ == '__main__':
    print("高级使用示例")
    print("注意: 请先修改 deploy_config.json 中的服务器信息")
    print("当前示例不会实际连接服务器")
    
    # 取消注释下面的行来运行示例
    # main()
