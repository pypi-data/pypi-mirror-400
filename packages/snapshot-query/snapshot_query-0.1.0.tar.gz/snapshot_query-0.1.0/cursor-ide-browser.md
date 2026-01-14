# Cursor IDE Browser 工具完整文档

## 📋 概述

**cursor-ide-browser** 是一个基于 MCP (Model Context Protocol) 的浏览器自动化工具，允许 AI 助手在 Cursor IDE 中直接与网页进行交互。该工具通过可访问性快照（Accessibility Snapshot）机制实现精确的元素定位和操作。

---

## 🏗️ 架构与实现

### 技术架构

```
AI 助手 (Auto)
  ↓ (MCP 协议)
MCP Server (cursor-ide-browser)
  ↓ (浏览器 API)
实际浏览器实例 (嵌入在 Cursor IDE 中)
```

### 核心机制

1. **可访问性快照（Accessibility Snapshot）**
   - 使用浏览器的 Accessibility API
   - 获取 DOM 的可访问性树（Accessibility Tree）
   - 包含所有可交互元素的语义信息
   - 比截图更准确，更适合程序化操作

2. **元素引用系统**
   - 每个元素有两个标识符：
     - `element`: 人类可读的描述（用于权限确认）
     - `ref`: 精确的技术引用（从快照中获取）
   - `ref` 是稳定的元素标识符，即使页面动态变化也能准确定位

3. **权限验证机制**
   - 每次交互需要提供 `element` 描述
   - 用于向用户展示将要执行的操作
   - 确保操作透明和安全

4. **多标签页管理**
   - 通过 `viewId` 管理多个浏览器标签页
   - 每个标签页有唯一标识符
   - 默认使用最后交互的标签页

---

## 🛠️ 工具列表

### 1. 导航相关

#### browser_navigate
导航到指定的 URL。

**参数：**
- `url` (string, 必需): 目标 URL
- `viewId` (string, 可选): 浏览器标签 ID。如果省略，使用最后交互的标签
- `position` (string, 可选): 
  - `"active"` (默认): 在当前编辑器组打开
  - `"side"`: 在侧边面板打开（当用户提到 "side"、"beside"、"side panel" 时使用）

**示例：**
```javascript
browser_navigate(url="https://example.com", position="side")
```

---

#### browser_navigate_back
返回到上一页。

**参数：**
- `viewId` (string, 可选): 浏览器标签 ID。如果省略，使用最后交互的标签

**示例：**
```javascript
browser_navigate_back()
```

---

### 2. 页面信息获取

#### browser_snapshot
捕获当前页面的可访问性快照。这是执行操作前的重要步骤，比截图更适合用于操作。

**参数：**
- `viewId` (string, 可选): 浏览器标签 ID。如果省略，使用最后交互的标签

**返回：**
- 页面的可访问性树结构
- 包含所有可交互元素的引用（ref）
- 元素的角色、名称、状态等信息
- 快照数据会同时保存到本地日志文件

**示例：**
```javascript
browser_snapshot()
```

**注意：** 这是执行任何交互操作前必须的步骤，用于获取元素的精确引用。

**快照日志文件：**
- 每次调用 `browser_snapshot()` 时，快照数据会保存到本地日志文件
- 文件路径：`C:\Users\{用户名}\.cursor\browser-logs\snapshot-{timestamp}.log`
- 文件名格式：`snapshot-{ISO 8601 timestamp}.log`（例如：`snapshot-2026-01-09T15-00-42-849Z.log`）
- 文件格式：YAML 格式，包含完整的可访问性树结构

---

#### browser_take_screenshot
截取页面截图。

**参数：**
- `type` (string, 可选): 图片格式，默认为 `"png"`
- `filename` (string, 可选): 保存的文件名。默认为 `page-{timestamp}.{png|jpeg}`
- `element` (string, 可选): 元素描述（如果要截取特定元素）
- `ref` (string, 可选): CSS 选择器（如果要截取特定元素）
- `fullPage` (boolean, 可选): 是否截取完整可滚动页面，默认为 `false`
- `viewId` (string, 可选): 浏览器标签 ID

**示例：**
```javascript
// 截取整个页面
browser_take_screenshot(fullPage=true)

// 截取特定元素
browser_take_screenshot(element="登录表单", ref="form#login")
```

---

#### browser_console_messages
返回所有控制台消息。

**参数：**
- `viewId` (string, 可选): 浏览器标签 ID

**返回：**
- 页面加载后的所有控制台消息
- 包括错误、警告、日志等

**示例：**
```javascript
browser_console_messages()
```

---

#### browser_network_requests
返回页面加载后的所有网络请求。

**参数：**
- `viewId` (string, 可选): 浏览器标签 ID

**返回：**
- 所有网络请求的详细信息
- 包括 URL、方法、状态码、响应等

**示例：**
```javascript
browser_network_requests()
```

---

### 3. 元素交互

#### browser_click
点击页面元素。

**参数：**
- `element` (string, 必需): 元素描述（用于获取权限）
- `ref` (string, 必需): 从页面快照中获取的精确元素引用
- `doubleClick` (boolean, 可选): 是否双击，默认为 `false`
- `button` (string, 可选): 点击的按钮，默认为 `"left"`
- `modifiers` (array, 可选): 修饰键数组（如 `["Control", "Shift"]`）
- `viewId` (string, 可选): 浏览器标签 ID

**示例：**
```javascript
browser_click(
  element="登录按钮",
  ref="button#login-btn",
  doubleClick=false
)
```

---

#### browser_type
在可编辑元素中输入文本。

**参数：**
- `element` (string, 必需): 元素描述（用于获取权限）
- `ref` (string, 必需): 从页面快照中获取的精确元素引用
- `text` (string, 必需): 要输入的文本
- `submit` (boolean, 可选): 是否提交（按 Enter），默认为 `false`
- `slowly` (boolean, 可选): 是否逐字符输入（用于触发按键处理器），默认为 `false`
- `viewId` (string, 可选): 浏览器标签 ID

**示例：**
```javascript
// 普通输入
browser_type(
  element="用户名输入框",
  ref="input#username",
  text="myusername"
)

// 输入并提交
browser_type(
  element="搜索框",
  ref="input#search",
  text="查询内容",
  submit=true
)

// 逐字符输入（触发按键事件）
browser_type(
  element="代码编辑器",
  ref="textarea#code",
  text="console.log('hello')",
  slowly=true
)
```

---

#### browser_hover
悬停在元素上。

**参数：**
- `element` (string, 必需): 元素描述（用于获取权限）
- `ref` (string, 必需): 从页面快照中获取的精确元素引用
- `viewId` (string, 可选): 浏览器标签 ID

**示例：**
```javascript
browser_hover(
  element="菜单项",
  ref="li.menu-item"
)
```

---

#### browser_select_option
在下拉菜单中选择选项。

**参数：**
- `element` (string, 必需): 元素描述（用于获取权限）
- `ref` (string, 必需): 从页面快照中获取的精确元素引用
- `values` (array, 必需): 要选择的值数组（可以是单选或多选）
- `viewId` (string, 可选): 浏览器标签 ID

**示例：**
```javascript
// 单选
browser_select_option(
  element="国家选择下拉框",
  ref="select#country",
  values=["USA"]
)

// 多选
browser_select_option(
  element="标签选择器",
  ref="select#tags",
  values=["tag1", "tag2", "tag3"]
)
```

---

#### browser_press_key
按下键盘按键。

**参数：**
- `key` (string, 必需): 按键名称（如 `"ArrowLeft"` 或字符如 `"a"`）
- `viewId` (string, 可选): 浏览器标签 ID

**示例：**
```javascript
// 按下方向键
browser_press_key(key="ArrowLeft")

// 按下字符
browser_press_key(key="a")

// 按下组合键（需要多次调用）
browser_press_key(key="Control")
browser_press_key(key="c")
```

---

### 4. 等待与同步

#### browser_wait_for
等待文本出现或消失，或等待指定时间。

**参数：**
- `time` (number, 可选): 等待时间（秒）
- `text` (string, 可选): 等待出现的文本
- `textGone` (string, 可选): 等待消失的文本
- `viewId` (string, 可选): 浏览器标签 ID

**注意：** 至少需要提供 `time`、`text` 或 `textGone` 中的一个。

**示例：**
```javascript
// 等待文本出现
browser_wait_for(text="加载完成")

// 等待文本消失
browser_wait_for(textGone="加载中...")

// 等待指定时间
browser_wait_for(time=3)

// 等待文本出现，最多等待5秒
browser_wait_for(text="页面已加载", time=5)
```

---

### 5. 窗口管理

#### browser_resize
调整浏览器窗口大小。

**参数：**
- `width` (number, 必需): 窗口宽度
- `height` (number, 必需): 窗口高度
- `viewId` (string, 可选): 浏览器标签 ID

**示例：**
```javascript
browser_resize(width=1920, height=1080)
```

---

#### browser_tabs
列出、创建、关闭或选择浏览器标签页。

**参数：**
- `action` (string, 必需): 操作类型
  - `"list"`: 列出所有标签页
  - `"new"`: 创建新标签页
  - `"close"`: 关闭标签页
  - `"select"`: 选择标签页
- `index` (number, 可选): 
  - 对于 `"select"`: 必需，要选择的标签索引
  - 对于 `"close"`: 可选，默认关闭当前标签
- `position` (string, 可选): 仅用于 `"new"` 操作
  - `"active"` (默认): 在当前编辑器组打开
  - `"side"`: 在侧边面板打开

**示例：**
```javascript
// 列出所有标签页
browser_tabs(action="list")

// 创建新标签页
browser_tabs(action="new", position="side")

// 选择标签页
browser_tabs(action="select", index=0)

// 关闭当前标签页
browser_tabs(action="close")
```

---

## 📄 快照日志文件格式

### 文件位置

快照日志文件保存在以下目录：
```
C:\Users\{用户名}\.cursor\browser-logs\
```

### 文件命名规则

文件名格式：`snapshot-{ISO 8601 timestamp}.log`

示例：
- `snapshot-2026-01-09T15-00-42-849Z.log`
- `snapshot-2026-01-09T16-30-15-123Z.log`

时间戳使用 ISO 8601 格式，包含：
- 日期：`YYYY-MM-DD`
- 时间：`HH-MM-SS-毫秒`
- 时区：`Z` (UTC)

### 文件格式

快照日志文件使用 **YAML 格式**，表示页面的可访问性树（Accessibility Tree）结构。

#### 基本结构

每个元素包含以下字段：

```yaml
- role: {元素角色}
  ref: {唯一引用标识符}
  name: {可选的元素名称/文本内容}
  children:
    - {子元素列表}
```

#### 字段说明

1. **`role`** (必需)
   - 元素的角色类型
   - 常见值：
     - `generic`: 通用容器元素
     - `link`: 链接
     - `button`: 按钮
     - `textbox`: 文本输入框
     - `img`: 图片
     - `list`: 列表
     - `listitem`: 列表项
     - `heading`: 标题
     - `pagedescription`: 页面描述
     - 等等（遵循 WAI-ARIA 角色规范）

2. **`ref`** (必需)
   - 元素的唯一引用标识符
   - 格式：`ref-{随机字符串}`
   - 示例：`ref-zketxgetcys`、`ref-b8rs5tdhk3e`
   - **重要**：这个 `ref` 值用于后续的元素交互操作（如 `browser_click`、`browser_type` 等）

3. **`name`** (可选)
   - 元素的名称或文本内容
   - 对于可访问性，这通常是屏幕阅读器会读取的内容
   - 可能包含：
     - 按钮文本
     - 链接文本
     - 输入框标签
     - 图片的 alt 文本
     - 其他可访问性文本

4. **`children`** (可选)
   - 子元素列表
   - 如果元素包含子元素，则会有此字段
   - 子元素遵循相同的结构

#### 示例

```yaml
- role: generic
  ref: ref-zketxgetcys
  children:
    - role: img
      ref: ref-zd3798voq9
    - role: pagedescription
      name: 欢迎进入 腾讯网,盲人用户使用操作智能引导，请按快捷键Ctrl+Alt+R；阅读详细操作说明请按快捷键Ctrl+Alt+问号键。
      ref: ref-us13t9giybd
      children:
        - role: img
          ref: ref-z0obxnpx1y
    - role: generic
      ref: ref-p37ecs217hp
      children:
        - role: generic
          ref: ref-6z2ca9bkkxf
          children:
            - role: generic
              ref: ref-wuz1gvkset
              children:
                - role: generic
                  ref: ref-62u5o5sunu
                  children:
                    - role: generic
                      ref: ref-r2kez4jj9y
                      children:
                        - role: link
                          ref: ref-mzigpg3ijr
                    - role: generic
                      ref: ref-zhx4wavxy6q
                      children:
                        - role: generic
                          ref: ref-sh2bokrxotn
                          children:
                            - role: textbox
                              ref: ref-b8rs5tdhk3e
                            - role: button
                              name: 搜索
                              ref: ref-b9k8zlttiah
                              children:
                                - role: img
                                  ref: ref-z4ue1duqv2
```

### 文件大小

- 快照文件的大小取决于页面的复杂度
- 简单页面：几 KB 到几十 KB
- 复杂页面（如新闻门户）：可能达到 100+ KB
- 示例：腾讯网首页快照约 88 KB（1590 行）

### 使用场景

1. **调试页面结构**
   - 查看页面的完整可访问性树
   - 理解页面元素层次结构
   - 查找特定元素的引用

2. **元素定位**
   - 从快照文件中提取 `ref` 值
   - 用于后续的交互操作

3. **页面分析**
   - 分析页面的可访问性
   - 检查元素的角色和名称
   - 验证页面结构

4. **历史记录**
   - 保存页面快照的历史记录
   - 可以对比不同时间点的页面状态

### 注意事项

1. **文件数量**
   - 每次调用 `browser_snapshot()` 都会创建新文件
   - 长时间使用可能产生大量日志文件
   - 建议定期清理旧日志文件

2. **文件读取**
   - 可以使用任何文本编辑器打开 `.log` 文件
   - YAML 格式便于阅读和解析
   - 可以使用 YAML 解析器进行程序化处理

3. **引用有效期**
   - `ref` 值仅在当前页面状态下有效
   - 页面刷新或导航后，`ref` 值会失效
   - 需要重新获取快照以获取新的 `ref` 值

4. **隐私和安全**
   - 快照文件可能包含页面内容
   - 注意保护敏感信息
   - 不要将包含敏感信息的快照文件分享给他人

### 高效查询和操作方法

> **快速参考**：详细查询指南请查看 [SNAPSHOT_QUERY_GUIDE.md](./SNAPSHOT_QUERY_GUIDE.md)

#### 1. 使用命令行工具（推荐）

我们提供了一个 Python 查询工具 `query_snapshot.py`，可以高效查询快照文件：

**安装依赖：**
```bash
pip install pyyaml
```

**工具位置**：项目根目录下的 `query_snapshot.py` 或使用 `uvx` 运行

**安装方式：**

1. **使用 uvx（推荐，从本地项目运行）**：
   ```bash
   uvx --from . snapshot-query <文件路径> <命令> [参数]
   ```
   
   **注意**：如果工具已发布到 PyPI，可以直接使用：
   ```bash
   uvx snapshot-query <文件路径> <命令> [参数]
   ```

2. **使用 pip 安装**：
   ```bash
   pip install snapshot-query
   snapshot-query <文件路径> <命令> [参数]
   ```

3. **直接运行脚本**：
   ```bash
   python query_snapshot.py <文件路径> <命令> [参数]
   ```

**基本用法：**

使用 uvx（推荐）：
```bash
# 根据名称查找元素（模糊匹配）
uvx --from . snapshot-query snapshot-2026-01-09T15-00-42-849Z.log find-name "搜索"

# 根据名称查找元素（精确匹配）
uvx --from . snapshot-query snapshot-2026-01-09T15-00-42-849Z.log find-name-exact "搜索"

# 根据角色查找元素
uvx --from . snapshot-query snapshot-2026-01-09T15-00-42-849Z.log find-role button

# 根据引用标识符查找元素
uvx --from . snapshot-query snapshot-2026-01-09T15-00-42-849Z.log find-ref ref-b9k8zlttiah

# 查找包含指定文本的元素
uvx --from . snapshot-query snapshot-2026-01-09T15-00-42-849Z.log find-text "登录"

# 列出所有可交互元素
uvx --from . snapshot-query snapshot-2026-01-09T15-00-42-849Z.log interactive

# 统计各类型元素数量
uvx --from . snapshot-query snapshot-2026-01-09T15-00-42-849Z.log count

# 显示元素在树中的路径
uvx --from . snapshot-query snapshot-2026-01-09T15-00-42-849Z.log path ref-b9k8zlttiah

# 列出所有引用标识符
uvx --from . snapshot-query snapshot-2026-01-09T15-00-42-849Z.log all-refs
```

或者使用传统方式：
```bash
# 使用 Python 模块方式
python -m snapshot_query snapshot.log find-name "搜索"

# 使用原始脚本
python query_snapshot.py snapshot.log find-name "搜索"
```

#### 2. 使用 grep/ripgrep 快速搜索

对于简单的文本搜索，可以使用命令行工具：

**Windows (PowerShell):**
```powershell
# 查找包含特定文本的行
Select-String -Path "snapshot-*.log" -Pattern "搜索"

# 查找所有按钮
Select-String -Path "snapshot-*.log" -Pattern "role: button"

# 查找所有引用标识符
Select-String -Path "snapshot-*.log" -Pattern "ref: ref-" | Select-Object -ExpandProperty Line
```

**Linux/Mac:**
```bash
# 查找包含特定文本的行
grep "搜索" snapshot-*.log

# 查找所有按钮
grep "role: button" snapshot-*.log

# 查找所有引用标识符
grep -o "ref: ref-[a-z0-9]*" snapshot-*.log
```

#### 3. 使用代码查询（Python 示例）

```python
import yaml

# 加载快照文件
with open('snapshot-2026-01-09T15-00-42-849Z.log', 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

# 查找所有按钮
def find_buttons(items):
    buttons = []
    for item in items:
        if item.get('role') == 'button':
            buttons.append(item)
        if 'children' in item:
            buttons.extend(find_buttons(item['children']))
    return buttons

buttons = find_buttons(data)
for button in buttons:
    print(f"按钮: {button.get('name', 'N/A')}, ref: {button.get('ref')}")

# 根据名称查找元素
def find_by_name(items, name):
    results = []
    for item in items:
        if 'name' in item and name in item['name']:
            results.append(item)
        if 'children' in item:
            results.extend(find_by_name(item['children'], name))
    return results

search_results = find_by_name(data, "登录")
for result in search_results:
    print(f"找到: {result.get('name')}, ref: {result.get('ref')}")
```

#### 4. 使用 VS Code / Cursor 搜索

在编辑器中打开快照文件，使用内置搜索功能：

- **按名称搜索**：`Ctrl+F` 搜索 `name: 搜索`
- **按角色搜索**：`Ctrl+F` 搜索 `role: button`
- **按引用搜索**：`Ctrl+F` 搜索 `ref: ref-xxxxx`
- **使用正则表达式**：启用正则模式，搜索 `ref: ref-[a-z0-9]+`

#### 5. 常用查询模式

**查找特定按钮的 ref：**
```bash
# 方法1: 使用 uvx
uvx --from . snapshot-query snapshot.log find-name "登录"

# 方法2: 使用 Python 模块
python -m snapshot_query snapshot.log find-name "登录"

# 方法3: 使用原始脚本
python query_snapshot.py snapshot.log find-name "登录"

# 方法4: 使用 grep
grep -A 2 "name: 登录" snapshot.log | grep "ref:"
```

**查找所有可点击元素：**
```bash
uvx --from . snapshot-query snapshot.log interactive
```

**统计页面元素：**
```bash
uvx --from . snapshot-query snapshot.log count
```

**查找元素路径（用于理解页面结构）：**
```bash
uvx --from . snapshot-query snapshot.log path ref-xxxxx
```

#### 6. 性能优化建议

1. **对于大文件**：使用 `grep` 或 `ripgrep` 比加载整个 YAML 文件更快
2. **批量查询**：使用 Python 脚本一次性处理多个查询
3. **索引构建**：对于频繁查询，可以构建索引文件（ref -> 元素信息映射）
4. **缓存结果**：将常用查询结果缓存，避免重复解析

#### 7. 实用脚本示例

**快速提取所有按钮的 ref：**
```python
import yaml
import re

with open('snapshot.log', 'r') as f:
    content = f.read()

# 使用正则表达式快速提取
buttons = re.findall(r'role: button\n\s+name: ([^\n]+)\n\s+ref: (ref-[^\n]+)', content)
for name, ref in buttons:
    print(f"{name}: {ref}")
```

**或者使用查询工具：**
```bash
python query_snapshot.py snapshot.log find-role button
```

**批量处理多个快照文件：**
```python
from pathlib import Path
import yaml

log_dir = Path(r"C:\Users\{用户名}\.cursor\browser-logs")

for log_file in log_dir.glob("snapshot-*.log"):
    print(f"\n处理文件: {log_file.name}")
    with open(log_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    # 执行查询操作...
```

---

## 🔄 标准使用流程

### 基本操作流程

1. **导航到页面**
   ```javascript
   browser_navigate(url="https://example.com")
   ```

2. **获取页面快照**
   ```javascript
   browser_snapshot()
   ```
   这一步是必需的，用于获取元素的精确引用。

3. **与元素交互**
   使用快照中返回的 `ref` 进行交互：
   ```javascript
   browser_click(element="按钮", ref="从快照获取的ref")
   browser_type(element="输入框", ref="从快照获取的ref", text="文本")
   ```

4. **等待内容加载**
   ```javascript
   browser_wait_for(text="某个文本")
   ```

5. **获取信息**
   ```javascript
   browser_take_screenshot()
   browser_console_messages()
   browser_network_requests()
   ```

### 完整示例

```javascript
// 1. 打开网页
browser_navigate(url="https://example.com/login", position="side")

// 2. 获取页面快照
const snapshot = browser_snapshot()

// 3. 输入用户名
browser_type(
  element="用户名输入框",
  ref="input#username",  // 从快照中获取
  text="myusername"
)

// 4. 输入密码
browser_type(
  element="密码输入框",
  ref="input#password",  // 从快照中获取
  text="mypassword"
)

// 5. 点击登录按钮
browser_click(
  element="登录按钮",
  ref="button#login"  // 从快照中获取
)

// 6. 等待登录完成
browser_wait_for(text="欢迎")

// 7. 截图确认
browser_take_screenshot(filename="login-success.png")
```

---

## 🎯 使用场景

### 1. 网页自动化测试
- 自动填写表单
- 测试用户流程
- 验证页面功能

### 2. 数据抓取
- 访问网页
- 提取信息
- 监控网络请求

### 3. 网页调试
- 查看控制台消息
- 分析网络请求
- 检查页面状态

### 4. 文档查询
- 访问在线文档
- 搜索信息
- 提取示例代码

### 5. 网页交互演示
- 展示操作流程
- 截图记录
- 自动化演示

---

## ⚠️ 注意事项与限制

### 1. 快照机制
- **必须先获取快照才能操作元素**
- 快照返回的元素引用（ref）是操作的关键
- 如果页面动态变化，可能需要重新获取快照

### 2. 动态内容
- 对于动态加载的内容，需要使用 `browser_wait_for()` 等待
- 某些单页应用（SPA）可能需要特殊处理

### 3. 安全限制
- 某些网站可能有安全策略阻止自动化操作
- 跨域限制可能影响某些操作
- 需要用户权限确认的操作可能无法自动化

### 4. 性能考虑
- 复杂页面的快照可能较慢
- 大量操作可能影响性能
- 建议在操作之间适当等待

### 5. 元素定位
- 必须使用快照返回的精确 `ref`
- 不能直接使用 CSS 选择器（除非在特定工具中支持）
- 元素引用在页面变化后可能失效

### 6. 多标签页
- 使用 `viewId` 管理多个标签页
- 默认操作最后交互的标签页
- 切换标签页需要使用 `browser_tabs(action="select")`

---

## 🔍 调试技巧

### 1. 查看页面状态
```javascript
// 获取快照查看当前页面结构
browser_snapshot()

// 查看控制台错误
browser_console_messages()

// 查看网络请求
browser_network_requests()
```

### 2. 截图调试
```javascript
// 在关键步骤截图
browser_take_screenshot(filename="step1.png")
// ... 执行操作
browser_take_screenshot(filename="step2.png")
```

### 3. 等待策略
```javascript
// 等待特定文本出现
browser_wait_for(text="加载完成", time=10)

// 等待加载指示器消失
browser_wait_for(textGone="加载中...")
```

### 4. 错误处理
- 如果操作失败，检查元素引用是否正确
- 确认页面是否已完全加载
- 检查是否有 JavaScript 错误（通过 console_messages）

---

## 🚀 最佳实践

### 1. 操作前准备
- 始终先获取快照
- 确认页面已加载完成
- 检查必要的元素是否存在

### 2. 交互顺序
- 按照用户正常操作顺序执行
- 在关键步骤之间适当等待
- 验证操作是否成功

### 3. 错误处理
- 使用 `browser_wait_for()` 处理异步操作
- 检查控制台消息排查问题
- 在失败时截图记录状态

### 4. 性能优化
- 避免不必要的快照
- 批量操作时适当等待
- 关闭不需要的标签页

### 5. 代码组织
- 将操作步骤模块化
- 使用清晰的元素描述
- 添加注释说明操作目的

---

## 📚 相关资源

### MCP 协议
- Model Context Protocol (MCP) 是用于 AI 助手与外部工具通信的协议
- cursor-ide-browser 是基于 MCP 实现的浏览器自动化服务器

### 可访问性 API
- 浏览器使用 Accessibility API 提供页面结构信息
- 这使得程序能够理解和操作网页内容

### 浏览器自动化
- 类似工具：Puppeteer、Playwright、Selenium
- cursor-ide-browser 专门为 Cursor IDE 和 AI 助手优化

---

## 🔄 更新日志

### 当前版本功能
- ✅ 完整的导航功能
- ✅ 元素交互（点击、输入、悬停等）
- ✅ 页面信息获取（快照、截图、控制台、网络）
- ✅ 多标签页管理
- ✅ 等待和同步机制
- ✅ 窗口管理
- ✅ 快照日志文件自动保存（YAML 格式）

---

## 💡 常见问题

### Q: 为什么需要先获取快照？
A: 快照提供了页面的结构化信息，包括所有可交互元素的精确引用。这些引用是执行操作所必需的。

### Q: 元素引用（ref）是什么格式？
A: ref 是从可访问性快照中获取的精确标识符，格式可能因实现而异，但通常是稳定的元素标识。

### Q: 如何处理动态加载的内容？
A: 使用 `browser_wait_for()` 等待特定文本出现或消失，或者等待指定时间。

### Q: 可以同时操作多个标签页吗？
A: 可以，使用 `viewId` 参数指定要操作的标签页，通过 `browser_tabs()` 管理多个标签页。

### Q: 截图和快照有什么区别？
A: 截图是视觉图像，用于查看页面外观。快照是结构化的可访问性信息，用于程序化操作。

### Q: 快照日志文件保存在哪里？
A: 快照日志文件保存在 `C:\Users\{用户名}\.cursor\browser-logs\` 目录下，文件名格式为 `snapshot-{timestamp}.log`。

### Q: 快照日志文件是什么格式？
A: 快照日志文件使用 YAML 格式，包含页面的可访问性树结构，每个元素包含 `role`、`ref`、`name`（可选）和 `children`（可选）字段。

### Q: 如何从快照文件中找到元素的 ref？
A: 在快照文件中搜索元素的 `name` 或相关文本，找到对应的元素后，其 `ref` 字段就是该元素的引用标识符，可以用于后续的交互操作。

---

## 📝 总结

cursor-ide-browser 是一个强大的浏览器自动化工具，通过 MCP 协议和可访问性 API 实现了精确的网页交互能力。它特别适合在 Cursor IDE 中与 AI 助手配合使用，实现网页自动化、数据抓取、调试和演示等功能。

关键要点：
- 使用快照机制获取页面结构
- 通过元素引用进行精确操作
- 支持多标签页管理
- 提供丰富的调试工具
- 遵循最佳实践确保稳定性

---

**文档版本**: 1.0.0  
**最后更新**: 2024  
**维护者**: Cursor IDE Team
