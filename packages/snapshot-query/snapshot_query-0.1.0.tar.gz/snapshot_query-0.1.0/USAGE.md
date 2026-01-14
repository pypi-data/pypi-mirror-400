# snapshot-query 使用指南

## 快速开始

### 方式1: 使用 uvx（推荐）

```bash
# 从本地项目运行
uvx --from . snapshot-query <文件路径> <命令> [参数]

# 示例
uvx --from . snapshot-query snapshot.log find-name "搜索"
```

### 方式2: 使用 Python 模块

```bash
python -m snapshot_query <文件路径> <命令> [参数]

# 示例
python -m snapshot_query snapshot.log find-name "搜索"
```

### 方式3: 使用原始脚本

```bash
# 需要先安装依赖
pip install pyyaml

# 运行脚本
python query_snapshot.py <文件路径> <命令> [参数]

# 示例
python query_snapshot.py snapshot.log find-name "搜索"
```

## 命令参考

### find-name
根据名称查找元素（模糊匹配）

```bash
uvx --from . snapshot-query snapshot.log find-name "搜索"
```

### find-name-exact
根据名称查找元素（精确匹配）

```bash
uvx --from . snapshot-query snapshot.log find-name-exact "搜索"
```

### find-role
根据角色查找元素

```bash
uvx --from . snapshot-query snapshot.log find-role button
```

### find-ref
根据引用标识符查找元素

```bash
uvx --from . snapshot-query snapshot.log find-ref ref-b9k8zlttiah
```

### find-text
查找包含指定文本的元素

```bash
uvx --from . snapshot-query snapshot.log find-text "登录"
```

### interactive
列出所有可交互元素

```bash
uvx --from . snapshot-query snapshot.log interactive
```

### count
统计各类型元素数量

```bash
uvx --from . snapshot-query snapshot.log count
```

### path
显示元素在树中的路径

```bash
uvx --from . snapshot-query snapshot.log path ref-b9k8zlttiah
```

### all-refs
列出所有引用标识符

```bash
uvx --from . snapshot-query snapshot.log all-refs
```

## 发布到 PyPI（可选）

如果你想将工具发布到 PyPI，让其他人可以直接使用 `uvx snapshot-query`：

1. **构建包**：
   ```bash
   pip install build
   python -m build
   ```

2. **发布到 PyPI**：
   ```bash
   pip install twine
   twine upload dist/*
   ```

3. **使用**：
   ```bash
   # 发布后，任何人都可以直接使用
   uvx snapshot-query snapshot.log find-name "搜索"
   ```
