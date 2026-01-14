# 快照日志文件查询快速指南

## 🚀 快速开始

### 使用 uvx（推荐，无需安装）

```bash
# 查找包含"登录"的元素
uvx snapshot-query snapshot.log find-name "登录"
```

### 使用 pip 安装

```bash
pip install snapshot-query
snapshot-query snapshot.log find-name "登录"
```

### 使用原始脚本

```bash
# 安装依赖
pip install pyyaml

# 运行脚本
python query_snapshot.py snapshot.log find-name "登录"
```

### 基本查询命令

# 查找所有按钮
uvx snapshot-query snapshot.log find-role button

# 查找特定 ref 的元素
uvx snapshot-query snapshot.log find-ref ref-b9k8zlttiah

# 列出所有可交互元素
uvx snapshot-query snapshot.log interactive

# 统计元素数量
uvx snapshot-query snapshot.log count
```

## 📋 常用查询场景

### 场景1: 找到按钮的 ref

**问题**：我想点击"搜索"按钮，需要找到它的 ref

**解决方案**：
```bash
uvx snapshot-query snapshot.log find-name "搜索"
```

**输出示例**：
```
找到 1 个匹配的元素:
role: button
ref: ref-b9k8zlttiah
name: 搜索
```

**使用**：
```javascript
browser_click(
  element="搜索按钮",
  ref="ref-b9k8zlttiah"
)
```

---

### 场景2: 找到所有可点击的元素

**问题**：我想看看页面上有哪些可交互的元素

**解决方案**：
```bash
uvx snapshot-query snapshot.log interactive
```

**输出示例**：
```
找到 50 个可交互元素:

button: 10 个
  role: button
  ref: ref-b9k8zlttiah
  name: 搜索

link: 30 个
  role: link
  ref: ref-jigeuju0z9
  name: 邮箱
...
```

---

### 场景3: 查找输入框

**问题**：我需要找到用户名输入框的 ref

**解决方案**：
```bash
# 方法1: 查找所有 textbox
uvx snapshot-query snapshot.log find-role textbox

# 方法2: 根据名称查找
uvx snapshot-query snapshot.log find-name "用户名"
```

---

### 场景4: 理解页面结构

**问题**：我想知道某个元素在页面中的位置

**解决方案**：
```bash
uvx snapshot-query snapshot.log path ref-b9k8zlttiah
```

**输出示例**：
```
元素路径:

层级 0:
  role: generic
  ref: ref-zketxgetcys

层级 1:
  role: generic
  ref: ref-p37ecs217hp

层级 2:
  role: generic
  ref: ref-zhx4wavxy6q

层级 3:
  role: button
  ref: ref-b9k8zlttiah
  name: 搜索
```

---

### 场景5: 批量查找链接

**问题**：我想找到所有包含"新闻"的链接

**解决方案**：
```bash
# 先查找包含"新闻"的元素
python query_snapshot.py snapshot.log find-text "新闻"

# 然后筛选出 link 类型的
python query_snapshot.py snapshot.log find-role link | grep "新闻"
```

---

## 🔧 高级用法

### 使用 Python 脚本进行复杂查询

```python
from query_snapshot import SnapshotQuery

# 加载快照文件
query = SnapshotQuery("snapshot-2026-01-09T15-00-42-849Z.log")

# 查找所有按钮
buttons = query.find_by_role("button")
print(f"找到 {len(buttons)} 个按钮")

# 查找包含"登录"的元素
login_elements = query.find_by_name("登录")
for elem in login_elements:
    print(f"名称: {elem.get('name')}, ref: {elem.get('ref')}")

# 获取元素路径
path = query.get_element_path("ref-b9k8zlttiah")
print(f"元素路径深度: {len(path)}")
```

### 使用 grep 快速搜索（适合大文件）

```bash
# Windows PowerShell
Select-String -Path "snapshot.log" -Pattern "name: 搜索" -Context 0,2

# Linux/Mac
grep -A 2 "name: 搜索" snapshot.log
```

### 提取所有 ref 到文件

```bash
python query_snapshot.py snapshot.log all-refs > refs.txt
```

## 📊 性能对比

| 方法 | 速度 | 适用场景 |
|------|------|----------|
| Python 工具 | 中等 | 复杂查询、需要解析结构 |
| grep/ripgrep | 快 | 简单文本搜索 |
| VS Code 搜索 | 中等 | 交互式查看和编辑 |

## 💡 实用技巧

1. **组合查询**：先用 `find-name` 找到大致位置，再用 `find-ref` 获取详细信息
2. **使用路径**：`path` 命令可以帮助理解页面结构
3. **批量处理**：对于多个快照文件，编写脚本批量处理
4. **缓存结果**：频繁查询的 ref 可以保存到配置文件

## 🎯 实际工作流示例

```bash
# 1. 获取页面快照（在浏览器中）
browser_snapshot()

# 2. 查找目标元素
uvx snapshot-query snapshot.log find-name "登录"

# 3. 获取 ref: ref-xxxxx

# 4. 使用 ref 进行操作
browser_click(element="登录按钮", ref="ref-xxxxx")
```

## 📝 常见问题

**Q: 为什么找不到元素？**
A: 检查元素名称是否正确，尝试使用模糊搜索 `find-name` 而不是精确搜索

**Q: ref 值会变化吗？**
A: 是的，每次页面刷新或重新获取快照，ref 值都会变化

**Q: 如何批量处理多个快照文件？**
A: 使用脚本循环处理：
```python
from pathlib import Path
from query_snapshot import SnapshotQuery

for log_file in Path(".cursor/browser-logs").glob("snapshot-*.log"):
    query = SnapshotQuery(log_file)
    # 执行查询...
```
