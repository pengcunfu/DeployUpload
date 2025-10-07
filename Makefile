# DeployUpload Makefile

.PHONY: help install install-dev test test-verbose test-coverage lint format clean build upload-test upload

# 默认目标
help:
	@echo "Available commands:"
	@echo "  install      - Install the package"
	@echo "  install-dev  - Install package with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-verbose - Run tests with verbose output"
	@echo "  test-coverage- Run tests with coverage report"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  upload-test  - Upload to test PyPI"
	@echo "  upload       - Upload to PyPI"

# 安装
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# 测试
test:
	pytest

test-verbose:
	pytest -v -s

test-coverage:
	pytest --cov=deployupload --cov-report=html --cov-report=term

# 代码质量
lint:
	flake8 deployupload tests examples

format:
	black deployupload tests examples

# 清理
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 构建
build: clean
	python -m build

# 发布
upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*

# 开发环境设置
setup-dev: install-dev
	pre-commit install
