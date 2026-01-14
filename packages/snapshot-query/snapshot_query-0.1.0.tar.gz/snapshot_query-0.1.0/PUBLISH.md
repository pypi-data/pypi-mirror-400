# 发布到 PyPI 指南

本指南说明如何将 `snapshot-query` 发布到 PyPI。

## 前置要求

1. **PyPI 账户**：
   - 在 [PyPI](https://pypi.org) 注册账户
   - 在 [TestPyPI](https://test.pypi.org) 注册账户（用于测试）

2. **安装构建工具**：
   ```bash
   pip install build twine
   ```

3. **配置认证**（推荐使用 API token）：
   - 在 PyPI 账户设置中创建 API token
   - 创建 `~/.pypirc` 文件（可选）：
     ```ini
     [distutils]
     index-servers =
         pypi
         testpypi

     [pypi]
     username = __token__
     password = pypi-你的API令牌

     [testpypi]
     username = __token__
     password = pypi-你的测试API令牌
     ```

## 发布步骤

### 1. 更新版本号

在发布新版本前，更新版本号：

- `pyproject.toml` 中的 `version` 字段
- `snapshot_query/__init__.py` 中的 `__version__` 变量

使用 [语义化版本](https://semver.org/)：
- `0.1.0` → `0.1.1` (补丁版本)
- `0.1.0` → `0.2.0` (小版本)
- `0.1.0` → `1.0.0` (主版本)

### 2. 清理旧的构建文件

```bash
# 删除旧的构建文件
rm -rf dist/
rm -rf build/
rm -rf *.egg-info
```

### 3. 构建分发包

```bash
# 使用 build 工具构建
python -m build
```

这将创建：
- `dist/snapshot-query-0.1.0.tar.gz` (源码分发包)
- `dist/snapshot_query-0.1.0-py3-none-any.whl` (wheel 分发包)

### 4. 检查分发包

```bash
# 检查分发包内容
twine check dist/*
```

### 5. 测试发布到 TestPyPI（推荐）

```bash
# 上传到 TestPyPI
twine upload --repository testpypi dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ snapshot-query
```

### 6. 发布到 PyPI

```bash
# 上传到 PyPI
twine upload dist/*
```

或者使用 API token：
```bash
twine upload --username __token__ --password pypi-你的API令牌 dist/*
```

### 7. 验证发布

```bash
# 等待几分钟让 PyPI 索引更新
pip install snapshot-query

# 测试安装
snapshot-query --help
```

## 完整发布命令序列

```bash
# 1. 清理
rm -rf dist/ build/ *.egg-info

# 2. 构建
python -m build

# 3. 检查
twine check dist/*

# 4. 测试发布（可选）
twine upload --repository testpypi dist/*

# 5. 正式发布
twine upload dist/*
```

## 使用 GitHub Actions 自动发布

可以创建 `.github/workflows/publish.yml` 来自动化发布流程：

```yaml
name: Publish to PyPI

on:
  release:
    types: [created]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

## 常见问题

### 1. 版本已存在错误

如果版本号已存在，需要更新版本号后重新构建和发布。

### 2. 认证失败

确保使用正确的 API token 或用户名/密码。

### 3. 文件大小限制

PyPI 对文件大小有限制（通常 60MB）。如果超过限制，考虑：
- 移除不必要的文件
- 使用 `MANIFEST.in` 控制包含的文件

## 发布检查清单

- [ ] 更新版本号
- [ ] 更新 CHANGELOG（如果有）
- [ ] 运行测试确保所有测试通过
- [ ] 检查 `pyproject.toml` 配置
- [ ] 构建分发包
- [ ] 检查分发包内容
- [ ] 测试安装（TestPyPI）
- [ ] 发布到 PyPI
- [ ] 验证安装和功能
