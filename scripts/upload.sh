#!/bin/bash

# 项目代码上传工具
# 适用于Linux和macOS系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示标题
echo "========================================"
echo "           项目代码上传工具"
echo "========================================"
echo

# 检查Python是否安装
print_info "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_error "未找到Python，请先安装Python 3.7+"
        print_info "Ubuntu/Debian: sudo apt install python3 python3-pip"
        print_info "CentOS/RHEL: sudo yum install python3 python3-pip"
        print_info "macOS: brew install python3"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

print_success "Python版本: $($PYTHON_CMD --version)"

# 检查依赖包
print_info "检查依赖包..."
if ! $PYTHON_CMD -c "import paramiko, tqdm" 2>/dev/null; then
    print_warning "依赖包未安装，正在安装..."
    
    # 检查pip
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        print_error "未找到pip，请先安装pip"
        exit 1
    fi
    
    PIP_CMD="pip3"
    if ! command -v pip3 &> /dev/null; then
        PIP_CMD="pip"
    fi
    
    print_info "使用 $PIP_CMD 安装依赖包..."
    $PIP_CMD install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        print_error "依赖包安装失败，请手动运行: $PIP_CMD install paramiko tqdm"
        exit 1
    fi
    
    print_success "依赖包安装完成！"
else
    print_success "依赖包检查完成！"
fi

echo

# 运行上传脚本
print_info "启动上传脚本..."
$PYTHON_CMD upload_simple.py

echo
print_success "脚本执行完成！" 