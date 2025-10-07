#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
提供简单的测试运行接口
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """运行命令并处理结果"""
    print(f"\n{'='*50}")
    print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("警告:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {e}")
        print("标准输出:", e.stdout)
        print("错误输出:", e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description='DeployUpload 测试运行器')
    parser.add_argument('--coverage', action='store_true', help='运行覆盖率测试')
    parser.add_argument('--lint', action='store_true', help='运行代码检查')
    parser.add_argument('--format', action='store_true', help='格式化代码')
    parser.add_argument('--all', action='store_true', help='运行所有检查')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--pattern', '-k', help='测试模式匹配')
    
    args = parser.parse_args()
    
    # 检查是否在项目根目录
    if not Path('deployupload').exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    success = True
    
    # 基本测试
    if not any([args.coverage, args.lint, args.format]) or args.all:
        cmd = ['python', '-m', 'pytest']
        if args.verbose:
            cmd.extend(['-v', '-s'])
        if args.pattern:
            cmd.extend(['-k', args.pattern])
        
        if not run_command(cmd, "基本测试"):
            success = False
    
    # 覆盖率测试
    if args.coverage or args.all:
        cmd = [
            'python', '-m', 'pytest',
            '--cov=deployupload',
            '--cov-report=html',
            '--cov-report=term',
            '--cov-fail-under=70'
        ]
        if args.verbose:
            cmd.extend(['-v'])
        
        if not run_command(cmd, "覆盖率测试"):
            success = False
    
    # 代码检查
    if args.lint or args.all:
        # Flake8检查
        if not run_command(
            ['python', '-m', 'flake8', 'deployupload', 'tests', 'examples'],
            "Flake8 代码检查"
        ):
            success = False
        
        # Black格式检查
        if not run_command(
            ['python', '-m', 'black', '--check', 'deployupload', 'tests', 'examples'],
            "Black 格式检查"
        ):
            success = False
    
    # 代码格式化
    if args.format:
        if not run_command(
            ['python', '-m', 'black', 'deployupload', 'tests', 'examples'],
            "Black 代码格式化"
        ):
            success = False
    
    # 总结
    print(f"\n{'='*50}")
    if success:
        print("🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
