# Pytest 使用指南

本指南介绍如何使用 pytest 为 snapshot-query 项目编写和运行测试。

## 目录

1. [Pytest 简介](#pytest-简介)
2. [安装和配置](#安装和配置)
3. [基本用法](#基本用法)
4. [测试结构](#测试结构)
5. [Fixtures](#fixtures)
6. [断言](#断言)
7. [参数化测试](#参数化测试)
8. [Mock 和 Patch](#mock-和-patch)
9. [测试覆盖率](#测试覆盖率)
10. [最佳实践](#最佳实践)

## Pytest 简介

Pytest 是 Python 最流行的测试框架之一，具有以下特点：

- **简单易用**：编写测试就像编写普通函数一样简单
- **功能强大**：支持 fixtures、参数化、mock 等高级特性
- **丰富的插件生态**：支持覆盖率、性能测试、并行执行等
- **清晰的错误信息**：提供详细的失败原因和堆栈跟踪

## 安装和配置

### 安装 pytest

```bash
# 使用 pip
pip install pytest pytest-cov

# 使用 uv
uv pip install pytest pytest-cov

# 安装开发依赖（包含 pytest）
pip install -e ".[dev]"
```

### 配置文件

项目使用 `pytest.ini` 进行配置：

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

## 基本用法

### 编写测试

测试文件以 `test_` 开头，测试函数以 `test_` 开头：

```python
# tests/test_example.py
def test_addition():
    assert 1 + 1 == 2

def test_string_concatenation():
    assert "hello" + " " + "world" == "hello world"
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_models.py

# 运行特定测试
pytest tests/test_models.py::TestSnapshotElement::test_create_element

# 详细输出
pytest -v

# 显示 print 输出
pytest -s
```

## 测试结构

### 测试类

使用类组织相关测试：

```python
class TestSnapshotElement:
    """测试 SnapshotElement 模型"""
    
    def test_create_element(self):
        """测试创建元素"""
        element = SnapshotElement(role="button", ref="ref-1")
        assert element.role == "button"
    
    def test_name_validation(self):
        """测试名称验证"""
        element = SnapshotElement(role="button", ref="ref-1", name="测试")
        assert element.name == "测试"
```

### 测试组织

```
tests/
├── __init__.py          # 包初始化
├── conftest.py          # 共享 fixtures
├── test_models.py       # 模型测试
├── test_query.py        # 查询功能测试
└── test_cli.py          # CLI 测试
```

## Fixtures

Fixtures 是 pytest 的核心特性，用于提供测试数据和设置/清理。

### 定义 Fixture

在 `conftest.py` 中定义共享 fixtures：

```python
import pytest
import yaml
from pathlib import Path

@pytest.fixture
def sample_snapshot_data():
    """创建示例快照数据"""
    return [
        {
            "role": "button",
            "ref": "ref-1",
            "name": "测试按钮"
        }
    ]

@pytest.fixture
def sample_snapshot_file(sample_snapshot_data, tmp_path):
    """创建临时快照文件"""
    snapshot_file = tmp_path / "test-snapshot.log"
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        yaml.dump(sample_snapshot_data, f, allow_unicode=True)
    return str(snapshot_file)
```

### 使用 Fixture

在测试函数中通过参数使用 fixture：

```python
def test_find_by_name(sample_snapshot_file):
    """测试按名称查找"""
    query = SnapshotQuery(sample_snapshot_file)
    results = query.find_by_name("测试")
    assert len(results) > 0
```

### Fixture 作用域

- `function`（默认）：每个测试函数执行一次
- `class`：每个测试类执行一次
- `module`：每个测试模块执行一次
- `session`：整个测试会话执行一次

```python
@pytest.fixture(scope="session")
def expensive_setup():
    """昂贵的设置，只执行一次"""
    return expensive_operation()
```

### 内置 Fixtures

- `tmp_path`：临时目录路径（Path 对象）
- `tmpdir`：临时目录（已弃用，使用 tmp_path）
- `capsys`：捕获 stdout/stderr
- `monkeypatch`：临时修改环境变量、函数等

## 断言

Pytest 使用 Python 的 `assert` 语句，失败时会显示详细信息：

```python
def test_assertions():
    # 基本断言
    assert 1 + 1 == 2
    
    # 包含断言
    assert "test" in "this is a test"
    
    # 类型断言
    assert isinstance([1, 2, 3], list)
    
    # 异常断言
    with pytest.raises(ValueError):
        int("not a number")
    
    # 异常消息断言
    with pytest.raises(ValueError, match="invalid"):
        raise ValueError("invalid input")
```

### 自定义断言消息

```python
def test_with_message():
    result = some_function()
    assert result is not None, "函数应该返回非 None 值"
```

## 参数化测试

使用 `@pytest.mark.parametrize` 运行同一测试的多个变体：

```python
@pytest.mark.parametrize("input,expected", [
    ("搜索", True),
    ("登录", True),
    ("不存在", False),
])
def test_find_by_name(input, expected, sample_snapshot_file):
    query = SnapshotQuery(sample_snapshot_file)
    results = query.find_by_name(input)
    assert (len(results) > 0) == expected
```

### 多个参数

```python
@pytest.mark.parametrize("role,count", [
    ("button", 2),
    ("link", 2),
    ("textbox", 1),
])
def test_count_by_role(role, count, sample_snapshot_file):
    query = SnapshotQuery(sample_snapshot_file)
    results = query.find_by_role(role)
    assert len(results) == count
```

## Mock 和 Patch

使用 `unittest.mock` 来模拟外部依赖：

```python
from unittest.mock import patch, MagicMock

def test_cli_with_mock(sample_snapshot_file, capsys):
    """测试 CLI 使用 mock"""
    with patch('sys.argv', ['snapshot-query', sample_snapshot_file, 'count']):
        main()
        captured = capsys.readouterr()
        assert "button" in captured.out
```

### Mock 对象

```python
def test_with_mock():
    mock_obj = MagicMock()
    mock_obj.method.return_value = "mocked result"
    assert mock_obj.method() == "mocked result"
    mock_obj.method.assert_called_once()
```

## 测试覆盖率

### 安装覆盖率工具

```bash
pip install pytest-cov
```

### 运行覆盖率测试

```bash
# 终端报告
pytest --cov=snapshot_query --cov-report=term-missing

# HTML 报告
pytest --cov=snapshot_query --cov-report=html
# 打开 htmlcov/index.html 查看报告
```

### 覆盖率配置

在 `pytest.ini` 中配置：

```ini
addopts = 
    --cov=snapshot_query
    --cov-report=term-missing
    --cov-report=html
```

## 最佳实践

### 1. 测试命名

- 测试文件：`test_*.py`
- 测试类：`Test*`
- 测试函数：`test_*`
- 使用描述性名称：`test_find_by_name_fuzzy` 而不是 `test1`

### 2. 测试独立性

每个测试应该独立，不依赖其他测试的执行顺序：

```python
# 好的做法
def test_create_element():
    element = SnapshotElement(role="button", ref="ref-1")
    assert element.role == "button"

# 不好的做法（依赖全局状态）
global_element = None

def test_create_element():
    global global_element
    global_element = SnapshotElement(role="button", ref="ref-1")

def test_use_element():
    assert global_element.role == "button"  # 依赖上一个测试
```

### 3. 使用 Fixtures

使用 fixtures 而不是全局变量：

```python
# 好的做法
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_something(sample_data):
    assert sample_data["key"] == "value"
```

### 4. 测试边界情况

不仅要测试正常情况，还要测试边界情况：

```python
def test_find_by_name_empty_result(sample_snapshot_file):
    """测试查找不存在的名称"""
    query = SnapshotQuery(sample_snapshot_file)
    results = query.find_by_name("不存在的名称")
    assert len(results) == 0

def test_find_by_name_empty_file(empty_snapshot_file):
    """测试空文件"""
    query = SnapshotQuery(empty_snapshot_file)
    results = query.find_by_name("test")
    assert len(results) == 0
```

### 5. 清晰的断言消息

```python
# 好的做法
assert len(results) > 0, "应该找到至少一个匹配的元素"

# 更好的做法（pytest 会自动显示详细信息）
assert len(results) > 0
```

### 6. 测试文档字符串

为测试添加文档字符串说明测试目的：

```python
def test_find_by_name_fuzzy(sample_snapshot_file):
    """测试模糊名称查找，应该找到包含搜索词的所有元素"""
    query = SnapshotQuery(sample_snapshot_file)
    results = query.find_by_name("搜索")
    assert len(results) > 0
```

### 7. 组织测试

按功能组织测试，使用测试类：

```python
class TestSnapshotQuery:
    """测试 SnapshotQuery 类"""
    
    class TestFindByName:
        """测试按名称查找"""
        
        def test_fuzzy_match(self):
            """测试模糊匹配"""
            pass
        
        def test_exact_match(self):
            """测试精确匹配"""
            pass
```

### 8. 使用标记

使用 pytest 标记来分类测试：

```python
@pytest.mark.slow
def test_expensive_operation():
    """慢速测试"""
    pass

# 运行时跳过慢速测试
pytest -m "not slow"
```

## 常见问题

### Q: 如何跳过测试？

```python
@pytest.mark.skip(reason="功能尚未实现")
def test_future_feature():
    pass
```

### Q: 如何条件跳过？

```python
import sys

@pytest.mark.skipif(sys.version_info < (3, 8), reason="需要 Python 3.8+")
def test_python38_feature():
    pass
```

### Q: 如何预期测试失败？

```python
@pytest.mark.xfail(reason="已知问题，待修复")
def test_known_bug():
    assert False
```

### Q: 如何捕获输出？

```python
def test_output(capsys):
    print("Hello, World!")
    captured = capsys.readouterr()
    assert "Hello" in captured.out
```

### Q: 如何临时修改环境？

```python
def test_env_var(monkeypatch):
    monkeypatch.setenv("TEST_VAR", "test_value")
    assert os.getenv("TEST_VAR") == "test_value"
```

## 参考资源

- [Pytest 官方文档](https://docs.pytest.org/)
- [Pytest 最佳实践](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python Testing with pytest](https://pythontest.com/pytest-book/)（书籍）
