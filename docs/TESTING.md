# 测试指南

本文档介绍如何运行 DeployUpload 项目的测试。

## 快速开始

### 安装测试依赖

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 或者只安装测试依赖
pip install -e ".[test]"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并显示详细输出
pytest -v

# 运行特定测试文件
pytest tests/test_uploader.py

# 运行特定测试类
pytest tests/test_uploader.py::TestProjectUploaderInit

# 运行特定测试方法
pytest tests/test_uploader.py::TestProjectUploaderInit::test_init_with_default_port
```

## 使用测试脚本

我们提供了一个便捷的测试脚本：

```bash
# 运行基本测试
python run_tests.py

# 运行覆盖率测试
python run_tests.py --coverage

# 运行代码检查
python run_tests.py --lint

# 格式化代码
python run_tests.py --format

# 运行所有检查
python run_tests.py --all

# 详细输出
python run_tests.py --verbose

# 运行特定模式的测试
python run_tests.py -k "test_init"
```

## 使用 Makefile

如果你在 Unix 系统上，可以使用 Makefile：

```bash
# 安装开发依赖
make install-dev

# 运行测试
make test

# 运行详细测试
make test-verbose

# 运行覆盖率测试
make test-coverage

# 代码检查
make lint

# 格式化代码
make format

# 清理构建文件
make clean
```

## 测试覆盖率

运行覆盖率测试：

```bash
pytest --cov=deployupload --cov-report=html --cov-report=term
```

这将生成：
- 终端输出的覆盖率报告
- `htmlcov/` 目录中的 HTML 覆盖率报告

打开 `htmlcov/index.html` 查看详细的覆盖率报告。

## 使用 tox 进行多环境测试

```bash
# 安装 tox
pip install tox

# 运行所有环境的测试
tox

# 运行特定环境
tox -e py39

# 运行代码检查
tox -e lint

# 运行覆盖率测试
tox -e coverage
```

## 测试结构

```
tests/
├── __init__.py          # 测试包初始化
├── conftest.py          # pytest 配置和共享 fixtures
├── test_uploader.py     # ProjectUploader 类的测试
└── test_cli.py          # CLI 模块的测试
```

### 主要测试类

- `TestProjectUploaderInit`: 测试初始化
- `TestIgnorePatterns`: 测试忽略模式功能
- `TestArchiveCreation`: 测试压缩包创建
- `TestConnectionMethods`: 测试连接相关方法
- `TestFileUpload`: 测试文件上传功能
- `TestUploadAndExtract`: 测试完整上传和解压功能
- `TestErrorHandling`: 测试错误处理
- `TestIntegration`: 集成测试

## 编写新测试

### 使用 fixtures

```python
def test_my_feature(mock_uploader, temp_project_dir, progress_tracker):
    # mock_uploader: 模拟的上传器实例
    # temp_project_dir: 临时测试项目目录
    # progress_tracker: 进度跟踪器
    pass
```

### 测试标记

使用 pytest 标记来分类测试：

```python
import pytest

@pytest.mark.unit
def test_unit_feature():
    pass

@pytest.mark.integration
def test_integration_feature():
    pass

@pytest.mark.slow
def test_slow_feature():
    pass

@pytest.mark.network
def test_network_feature():
    pass
```

运行特定标记的测试：

```bash
# 只运行单元测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"

# 跳过需要网络的测试
pytest -m "not network"
```

## 持续集成

项目配置了 GitHub Actions 进行持续集成，会在以下情况下自动运行测试：

- 推送到 main 或 develop 分支
- 创建 Pull Request

CI 会在多个 Python 版本和操作系统上运行测试：
- Python: 3.7, 3.8, 3.9, 3.10, 3.11
- OS: Ubuntu, Windows, macOS

## 故障排除

### 常见问题

1. **导入错误**: 确保已安装包 `pip install -e .`
2. **权限错误**: 在 Windows 上可能需要管理员权限
3. **网络测试失败**: 使用 `-m "not network"` 跳过网络测试

### 调试测试

```bash
# 在第一个失败时停止
pytest -x

# 显示本地变量
pytest --tb=long

# 进入调试器
pytest --pdb

# 显示打印输出
pytest -s
```

## 性能测试

虽然当前没有专门的性能测试，但可以使用以下方式监控性能：

```bash
# 显示最慢的10个测试
pytest --durations=10

# 使用 pytest-benchmark（需要安装）
pip install pytest-benchmark
```

## 贡献测试

在提交代码时，请确保：

1. 所有测试通过
2. 代码覆盖率不降低
3. 新功能有相应的测试
4. 遵循现有的测试风格

```bash
# 提交前检查
python run_tests.py --all
```
