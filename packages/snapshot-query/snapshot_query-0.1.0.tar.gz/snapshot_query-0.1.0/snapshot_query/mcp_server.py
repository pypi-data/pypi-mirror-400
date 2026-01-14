"""
MCP 服务器接口
提供通过 Model Context Protocol 访问快照查询功能
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 尝试导入 MCP SDK，支持多种可能的导入路径
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    try:
        # 尝试替代导入路径
        from mcp import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
    except ImportError:
        # 如果 MCP SDK 未安装，提供友好的错误提示
        print("错误: 需要安装 MCP SDK。运行: pip install mcp", file=sys.stderr)
        print("或者: pip install @modelcontextprotocol/server-sdk-python", file=sys.stderr)
        sys.exit(1)

from .query import SnapshotQuery
from .models import SnapshotElement
from typing import Union


# 创建 MCP 服务器实例
server = Server("snapshot-query")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="find_by_name",
            description="根据元素名称查找元素（模糊匹配）",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "快照日志文件路径"
                    },
                    "name": {
                        "type": "string",
                        "description": "要搜索的元素名称"
                    },
                    "exact": {
                        "type": "boolean",
                        "description": "是否精确匹配，默认为 false（模糊匹配）",
                        "default": False
                    }
                },
                "required": ["file_path", "name"]
            }
        ),
        Tool(
            name="find_by_name_bm25",
            description="使用 BM25 算法根据元素名称查找元素（按相关性排序）",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "快照日志文件路径"
                    },
                    "name": {
                        "type": "string",
                        "description": "要搜索的元素名称"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回前 k 个最相关的结果，不提供则返回所有结果",
                        "minimum": 1
                    }
                },
                "required": ["file_path", "name"]
            }
        ),
        Tool(
            name="find_by_role",
            description="根据角色类型查找元素（如 button、link、textbox 等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "快照日志文件路径"
                    },
                    "role": {
                        "type": "string",
                        "description": "元素角色（button、link、textbox、checkbox 等）"
                    }
                },
                "required": ["file_path", "role"]
            }
        ),
        Tool(
            name="find_by_ref",
            description="根据引用标识符查找元素",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "快照日志文件路径"
                    },
                    "ref": {
                        "type": "string",
                        "description": "元素的引用标识符（如 ref-xxxxx）"
                    }
                },
                "required": ["file_path", "ref"]
            }
        ),
        Tool(
            name="find_by_text",
            description="查找包含指定文本的元素",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "快照日志文件路径"
                    },
                    "text": {
                        "type": "string",
                        "description": "要搜索的文本内容"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "是否区分大小写，默认为 false",
                        "default": False
                    }
                },
                "required": ["file_path", "text"]
            }
        ),
        Tool(
            name="find_by_regex",
            description="使用正则表达式（grep 语法）查找元素",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "快照日志文件路径"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "正则表达式模式（支持 grep 语法）"
                    },
                    "field": {
                        "type": "string",
                        "description": "要搜索的字段：'name'（默认）、'role' 或 'ref'",
                        "enum": ["name", "role", "ref"],
                        "default": "name"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "是否区分大小写，默认为 false",
                        "default": False
                    }
                },
                "required": ["file_path", "pattern"]
            }
        ),
        Tool(
            name="find_by_selector",
            description="使用 CSS/jQuery 选择器语法查找元素",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "快照日志文件路径"
                    },
                    "selector": {
                        "type": "string",
                        "description": "CSS/jQuery 选择器（如 button, #ref-xxx, button[name='搜索']）"
                    }
                },
                "required": ["file_path", "selector"]
            }
        ),
        Tool(
            name="find_interactive_elements",
            description="查找所有可交互元素（按钮、链接、输入框等）",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "快照日志文件路径"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="count_elements",
            description="统计各类型元素的数量",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "快照日志文件路径"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_element_path",
            description="获取元素在树中的路径",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "快照日志文件路径"
                    },
                    "ref": {
                        "type": "string",
                        "description": "元素的引用标识符"
                    }
                },
                "required": ["file_path", "ref"]
            }
        ),
        Tool(
            name="extract_all_refs",
            description="提取快照文件中所有元素的引用标识符",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "快照日志文件路径"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]


def format_element(element: Union[SnapshotElement, Dict[str, Any]]) -> str:
    """格式化元素信息为字符串"""
    lines = []
    
    # 支持 pydantic 模型和字典
    if isinstance(element, SnapshotElement):
        role = element.role
        ref = element.ref
        name = element.name or ''
        has_children = element.children is not None and len(element.children) > 0
        children_count = len(element.children) if element.children else 0
    else:
        role = element.get('role', 'unknown')
        ref = element.get('ref', 'N/A')
        name = element.get('name', '')
        has_children = 'children' in element
        children_count = len(element['children']) if has_children else 0
    
    lines.append(f"role: {role}")
    lines.append(f"ref: {ref}")
    if name:
        lines.append(f"name: {name}")
    if has_children:
        lines.append(f"children: {children_count} items")
    
    return "\n".join(lines)


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    file_path = arguments.get("file_path")
    
    if not file_path:
        return [TextContent(
            type="text",
            text="错误: 需要提供 file_path 参数"
        )]
    
    try:
        query = SnapshotQuery(file_path)
        result_text = ""
        
        if name == "find_by_name":
            name_param = arguments.get("name")
            exact = arguments.get("exact", False)
            if not name_param:
                return [TextContent(type="text", text="错误: 需要提供 name 参数")]
            
            results = query.find_by_name(name_param, exact=exact)
            result_text = f"找到 {len(results)} 个匹配的元素:\n\n"
            for item in results:
                result_text += format_element(item) + "\n\n"
        
        elif name == "find_by_name_bm25":
            name_param = arguments.get("name")
            top_k = arguments.get("top_k")
            if not name_param:
                return [TextContent(type="text", text="错误: 需要提供 name 参数")]
            
            results = query.find_by_name_bm25(name_param, top_k=top_k)
            result_text = f"找到 {len(results)} 个相关元素（按相关性排序）:\n\n"
            for item in results:
                result_text += format_element(item) + "\n\n"
        
        elif name == "find_by_role":
            role = arguments.get("role")
            if not role:
                return [TextContent(type="text", text="错误: 需要提供 role 参数")]
            
            results = query.find_by_role(role)
            result_text = f"找到 {len(results)} 个 {role} 元素:\n\n"
            for item in results[:20]:  # 限制输出数量
                result_text += format_element(item) + "\n\n"
            if len(results) > 20:
                result_text += f"... 还有 {len(results) - 20} 个元素未显示\n"
        
        elif name == "find_by_ref":
            ref = arguments.get("ref")
            if not ref:
                return [TextContent(type="text", text="错误: 需要提供 ref 参数")]
            
            result = query.find_by_ref(ref)
            if result:
                result_text = "找到元素:\n\n" + format_element(result)
            else:
                result_text = "未找到匹配的元素"
        
        elif name == "find_by_text":
            text = arguments.get("text")
            if not text:
                return [TextContent(type="text", text="错误: 需要提供 text 参数")]
            
            case_sensitive = arguments.get("case_sensitive", False)
            results = query.find_elements_with_text(text, case_sensitive=case_sensitive)
            result_text = f"找到 {len(results)} 个包含文本的元素:\n\n"
            for item in results[:20]:  # 限制输出数量
                result_text += format_element(item) + "\n\n"
            if len(results) > 20:
                result_text += f"... 还有 {len(results) - 20} 个元素未显示\n"
        
        elif name == "find_by_regex":
            pattern = arguments.get("pattern")
            field = arguments.get("field", "name")
            case_sensitive = arguments.get("case_sensitive", False)
            
            if not pattern:
                return [TextContent(type="text", text="错误: 需要提供 pattern 参数")]
            
            if field not in ["name", "role", "ref"]:
                return [TextContent(type="text", text=f"错误: field 必须是 'name', 'role' 或 'ref'，当前为: {field}")]
            
            try:
                results = query.find_by_regex(pattern, field=field, case_sensitive=case_sensitive)
                result_text = f"找到 {len(results)} 个匹配正则表达式 '{pattern}' 的元素 (字段: {field}):\n\n"
                for item in results[:20]:  # 限制输出数量
                    result_text += format_element(item) + "\n\n"
                if len(results) > 20:
                    result_text += f"... 还有 {len(results) - 20} 个元素未显示\n"
            except ValueError as e:
                return [TextContent(type="text", text=f"错误: {str(e)}")]
        
        elif name == "find_by_selector":
            selector = arguments.get("selector")
            
            if not selector:
                return [TextContent(type="text", text="错误: 需要提供 selector 参数")]
            
            try:
                results = query.find_by_selector(selector)
                result_text = f"找到 {len(results)} 个匹配选择器 '{selector}' 的元素:\n\n"
                for item in results[:20]:  # 限制输出数量
                    result_text += format_element(item) + "\n\n"
                if len(results) > 20:
                    result_text += f"... 还有 {len(results) - 20} 个元素未显示\n"
            except Exception as e:
                return [TextContent(type="text", text=f"错误: {str(e)}")]
        
        elif name == "find_interactive_elements":
            interactive = query.find_interactive_elements()
            total = sum(len(items) for items in interactive.values())
            result_text = f"找到 {total} 个可交互元素:\n\n"
            for role, items in interactive.items():
                if items:
                    result_text += f"{role}: {len(items)} 个\n"
                    for item in items[:5]:  # 每个类型只显示前5个
                        result_text += "  " + format_element(item).replace("\n", "\n  ") + "\n\n"
                    if len(items) > 5:
                        result_text += f"  ... 还有 {len(items) - 5} 个 {role} 元素\n\n"
        
        elif name == "count_elements":
            counts = query.count_elements()
            result_text = "元素统计:\n"
            for role, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
                result_text += f"  {role}: {count}\n"
        
        elif name == "get_element_path":
            ref = arguments.get("ref")
            if not ref:
                return [TextContent(type="text", text="错误: 需要提供 ref 参数")]
            
            path = query.get_element_path(ref)
            if path:
                result_text = "元素路径:\n\n"
                for i, element in enumerate(path):
                    result_text += f"层级 {i}:\n"
                    result_text += "  " + format_element(element).replace("\n", "\n  ") + "\n\n"
            else:
                result_text = "未找到匹配的元素"
        
        elif name == "extract_all_refs":
            refs = query.extract_all_refs()
            result_text = f"共 {len(refs)} 个引用标识符:\n"
            for ref in refs[:100]:  # 限制输出数量
                result_text += f"  {ref}\n"
            if len(refs) > 100:
                result_text += f"... 还有 {len(refs) - 100} 个引用标识符\n"
        
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
        
        return [TextContent(type="text", text=result_text)]
    
    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"错误: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"错误: {str(e)}")]


async def main():
    """运行 MCP 服务器"""
    # 使用 stdio 传输运行 MCP 服务器
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def run_server():
    """同步包装函数，用于命令行入口点"""
    asyncio.run(main())


if __name__ == "__main__":
    run_server()
