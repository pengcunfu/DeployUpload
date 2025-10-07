@echo off
chcp 65001 >nul
title 项目代码上传工具

echo ========================================
echo           项目代码上传工具
echo ========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查依赖包
echo 检查依赖包...
python -c "import paramiko, tqdm" >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 依赖包安装失败，请手动运行: pip install paramiko tqdm
        pause
        exit /b 1
    )
)

echo 依赖包检查完成！
echo.

REM 运行上传脚本
echo 启动上传脚本...
python upload_simple.py

echo.
echo 按任意键退出...
pause >nul 