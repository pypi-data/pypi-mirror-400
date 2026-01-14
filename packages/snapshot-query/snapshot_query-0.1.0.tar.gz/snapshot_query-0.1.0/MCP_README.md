# MCP 服务器接口使用指南

snapshot-query 提供了 MCP (Model Context Protocol) 服务器接口，允许 AI 助手通过标准化的协议查询快照文件。

## 安装

确保已安装 MCP SDK：

```bash
pip install mcp
```

或者使用官方 SDK：

```bash
pip install @modelcontextprotocol/server-sdk-python
```

## 启动 MCP 服务器

### 方式1: 使用命令行入口点

```bash
snapshot-query-mcp
```

### 方式2: 使用 Python 模块

```bash
python -m snapshot_query.mcp_server
```

### 方式3: 直接运行脚本

```bash
python snapshot_query/mcp_server.py
```

## 配置客户端

在 Cursor IDE 或其他 MCP 客户端中配置服务器。编辑 MCP 配置文件（通常在 `~/.cursor/mcp.json` 或类似位置）：

```json
{
  "mcpServers": {
    "snapshot-query": {
      "command": "snapshot-query-mcp",
      "args": []
    }
  }
}
```

或者使用 Python 模块方式：

```json
{
  "mcpServers": {
    "snapshot-query": {
      "command": "python",
      "args": ["-m", "snapshot_query.mcp_server"]
    }
  }
}
```

## 可用工具

MCP 服务器提供以下工具：

### 1. find_by_name
根据元素名称查找元素（支持模糊和精确匹配）

**参数：**
- `file_path` (string, 必需): 快照日志文件路径
- `name` (string, 必需): 要搜索的元素名称
- `exact` (boolean, 可选): 是否精确匹配，默认为 false

**示例：**
```json
{
  "file_path": "snapshot.log",
  "name": "搜索",
  "exact": false
}
```

### 2. find_by_role
根据角色类型查找元素

**参数：**
- `file_path` (string, 必需): 快照日志文件路径
- `role` (string, 必需): 元素角色（button、link、textbox 等）

**示例：**
```json
{
  "file_path": "snapshot.log",
  "role": "button"
}
```

### 3. find_by_ref
根据引用标识符查找元素

**参数：**
- `file_path` (string, 必需): 快照日志文件路径
- `ref` (string, 必需): 元素的引用标识符

**示例：**
```json
{
  "file_path": "snapshot.log",
  "ref": "ref-b9k8zlttiah"
}
```

### 4. find_by_text
查找包含指定文本的元素

**参数：**
- `file_path` (string, 必需): 快照日志文件路径
- `text` (string, 必需): 要搜索的文本内容
- `case_sensitive` (boolean, 可选): 是否区分大小写，默认为 false

**示例：**
```json
{
  "file_path": "snapshot.log",
  "text": "登录",
  "case_sensitive": false
}
```

### 5. find_interactive_elements
查找所有可交互元素

**参数：**
- `file_path` (string, 必需): 快照日志文件路径

**示例：**
```json
{
  "file_path": "snapshot.log"
}
```

### 6. count_elements
统计各类型元素的数量

**参数：**
- `file_path` (string, 必需): 快照日志文件路径

**示例：**
```json
{
  "file_path": "snapshot.log"
}
```

### 7. get_element_path
获取元素在树中的路径

**参数：**
- `file_path` (string, 必需): 快照日志文件路径
- `ref` (string, 必需): 元素的引用标识符

**示例：**
```json
{
  "file_path": "snapshot.log",
  "ref": "ref-b9k8zlttiah"
}
```

### 8. extract_all_refs
提取快照文件中所有元素的引用标识符

**参数：**
- `file_path` (string, 必需): 快照日志文件路径

**示例：**
```json
{
  "file_path": "snapshot.log"
}
```

## 使用场景

### 在 AI 助手中使用

配置好 MCP 服务器后，AI 助手可以直接调用这些工具来查询快照文件：

```
用户: 在 snapshot.log 中查找所有按钮
AI: [调用 find_by_role 工具，file_path="snapshot.log", role="button"]
```

### 与 cursor-ide-browser 配合使用

1. 使用 `browser_snapshot()` 获取页面快照
2. 快照保存为日志文件
3. 通过 MCP 接口查询快照文件，找到元素的 ref
4. 使用 ref 进行浏览器交互操作

## 故障排除

### MCP SDK 未安装

如果遇到导入错误，确保已安装 MCP SDK：

```bash
pip install mcp
```

### 服务器无法启动

检查 Python 环境是否正确，确保所有依赖已安装：

```bash
pip install -e .
```

### 客户端连接失败

- 检查 MCP 配置文件路径和格式
- 确保服务器命令路径正确
- 查看客户端日志获取详细错误信息

## 开发

MCP 服务器代码位于 `snapshot_query/mcp_server.py`。要添加新工具：

1. 在 `list_tools()` 中添加工具定义
2. 在 `call_tool()` 中添加工具处理逻辑
3. 使用 `SnapshotQuery` 类执行查询操作
