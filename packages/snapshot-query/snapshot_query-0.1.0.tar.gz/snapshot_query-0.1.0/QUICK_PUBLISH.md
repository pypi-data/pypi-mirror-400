# 快速发布指南

## 快速开始

### 1. 安装构建工具

```bash
pip install build twine
```

### 2. 构建分发包

```bash
# Windows PowerShell
.\scripts\publish.ps1

# Linux/Mac
bash scripts/publish.sh

# 或手动执行
python -m build
```

### 3. 检查分发包

```bash
twine check dist/*
```

### 4. 发布到 PyPI

```bash
# 使用 API token（推荐）
twine upload --username __token__ --password pypi-你的API令牌 dist/*

# 或使用配置文件
twine upload dist/*
```

## 发布前检查清单

- [ ] 更新版本号（`pyproject.toml` 和 `snapshot_query/__init__.py`）
- [ ] 运行测试：`pytest`
- [ ] 检查代码：确保没有语法错误
- [ ] 构建分发包：`python -m build`
- [ ] 检查分发包：`twine check dist/*`

## 版本号更新

发布新版本时，需要更新两个地方的版本号：

1. `pyproject.toml`:
   ```toml
   version = "0.1.1"  # 更新这里
   ```

2. `snapshot_query/__init__.py`:
   ```python
   __version__ = "0.1.1"  # 更新这里
   ```

## 测试发布（推荐）

在正式发布前，先发布到 TestPyPI 测试：

```bash
twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ snapshot-query
```

## 完整命令序列

```bash
# 1. 清理
rm -rf dist/ build/ *.egg-info

# 2. 构建
python -m build

# 3. 检查
twine check dist/*

# 4. 发布
twine upload dist/*
```
