# DeployUpload

一个用于将本地文件夹打包并上传到远程服务器的Python包。支持进度回调、.gitignore文件过滤等功能。

## 功能特性

- 🚀 **简单易用**: 只需几行代码即可完成文件夹打包上传
- 📦 **智能打包**: 自动忽略.gitignore和.deploy_ignore中指定的文件
- 📊 **进度回调**: 支持自定义进度回调函数，实时监控上传进度
- 🔒 **安全连接**: 使用SSH/SFTP协议安全传输文件
- 🎯 **灵活配置**: 支持自定义忽略模式和文件
- 📱 **命令行工具**: 提供便捷的命令行接口

## 安装

```bash
pip install deployupload
```

或者从源码安装：

```bash
git clone https://github.com/pengcunfu/DeployUpload.git
cd DeployUpload
pip install -e .
```

## 快速开始

### 基本使用

```python
from deployupload import ProjectUploader

# 创建上传器实例
uploader = ProjectUploader(
    host='192.168.1.100',
    username='ubuntu',
    password='your_password',
    port=22
)

# 上传项目文件夹
remote_path = uploader.upload_and_extract('/path/to/your/project')
print(f"项目已上传到: {remote_path}")
```

### 带进度回调的使用

```python
from deployupload import ProjectUploader

def my_progress_callback(stage, current, total):
    """自定义进度回调函数"""
    if total > 0:
        percent = (current / total) * 100
        print(f"{stage}: {percent:.1f}% ({current}/{total})")
    else:
        print(f"{stage}: {current}")

# 创建上传器
uploader = ProjectUploader('192.168.1.100', 'ubuntu', 'password')

# 带进度回调的上传
uploader.upload_and_extract(
    '/path/to/project',
    progress_callback=my_progress_callback
)
```

### 高级配置

```python
from deployupload import ProjectUploader

# 创建上传器
uploader = ProjectUploader('192.168.1.100', 'ubuntu', 'password')

# 设置额外的忽略模式
uploader.set_ignore_patterns(['*.log', 'temp/*', '*.tmp'])

# 设置额外的忽略文件
uploader.set_ignore_files(['/path/to/specific/file.txt'])

# 测试连接
if uploader.test_connection():
    print("服务器连接成功")
    
    # 只创建压缩包（不上传）
    archive_path = uploader.create_archive('/path/to/project')
    print(f"压缩包已创建: {archive_path}")
    
    # 只上传文件（不解压）
    remote_path = uploader.upload_file(archive_path)
    print(f"文件已上传到: {remote_path}")
else:
    print("服务器连接失败")
```

## 命令行使用

安装后可以直接使用命令行工具：

```bash
# 交互式使用
deployupload -i

# 直接指定参数
deployupload --host 192.168.1.100 --username ubuntu --password your_password

# 指定项目目录和远程目录
deployupload --host 192.168.1.100 --username ubuntu --password your_password \
             --project-root /path/to/project --remote-dir /home/ubuntu/projects
```

## API 文档

### ProjectUploader 类

#### 构造函数

```python
ProjectUploader(host, username, password, port=22)
```

**参数:**
- `host` (str): 服务器IP地址或域名
- `username` (str): 服务器用户名  
- `password` (str): 服务器密码
- `port` (int): SSH端口，默认为22

#### 主要方法

##### upload_and_extract()

打包、上传并解压项目文件夹。

```python
upload_and_extract(project_root, remote_dir=None, progress_callback=None)
```

**参数:**
- `project_root` (str): 项目根目录路径
- `remote_dir` (str, optional): 远程解压目录，默认为用户home目录
- `progress_callback` (callable, optional): 进度回调函数

**返回:** 远程项目目录路径

##### create_archive()

创建项目压缩包。

```python
create_archive(project_root, output_path=None, progress_callback=None)
```

**参数:**
- `project_root` (str): 项目根目录路径
- `output_path` (str, optional): 输出压缩包路径
- `progress_callback` (callable, optional): 进度回调函数

**返回:** 压缩包路径

##### upload_file()

上传文件到服务器。

```python
upload_file(local_path, remote_path=None, progress_callback=None)
```

**参数:**
- `local_path` (str): 本地文件路径
- `remote_path` (str, optional): 远程文件路径
- `progress_callback` (callable, optional): 进度回调函数

**返回:** 远程文件路径

##### test_connection()

测试服务器连接。

```python
test_connection()
```

**返回:** bool - 连接是否成功

## 忽略文件配置

DeployUpload 支持多种方式配置忽略文件：

### .gitignore 文件

自动读取项目中的所有 `.gitignore` 文件，支持标准的 gitignore 语法。

### .deploy_ignore 文件

专门用于部署时的忽略配置，语法与 `.gitignore` 相同。

### 代码配置

```python
# 设置忽略模式
uploader.set_ignore_patterns(['*.log', 'temp/*'])

# 设置忽略文件
uploader.set_ignore_files(['/path/to/file'])
```

## 进度回调

进度回调函数接收三个参数：

```python
def progress_callback(stage, current, total):
    """
    stage: 当前阶段名称 (str)
    current: 当前进度 (int)  
    total: 总进度 (int)
    """
    pass
```

可能的阶段包括：
- "收集忽略模式"
- "计算文件数量" 
- "复制文件"
- "创建压缩包"
- "连接服务器"
- "上传文件"
- "解压文件"

## 依赖要求

- Python >= 3.7
- paramiko >= 3.0.0
- tqdm >= 4.64.0

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0
- 初始版本发布
- 支持文件夹打包上传
- 支持进度回调
- 支持 .gitignore 文件过滤
- 提供命令行工具