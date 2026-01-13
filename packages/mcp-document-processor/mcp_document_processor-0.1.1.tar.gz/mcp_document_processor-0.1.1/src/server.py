import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.server import Server
from mcp.server.models import Tool
import mcp.server.stdio

# 创建 MCP 服务器
server = Server("document-processor-server")

@server.list_tools()
async def handle_list_tools():
    """返回可用的工具列表"""
    return [
        Tool(
            name="file_generate",
            description="文件生成方法",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "可选的名称参数"
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """处理工具调用"""
    if name == "file_generate":
        name_param = arguments.get("name", "World")
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"文件结果 {name_param}!"
                }
            ]
        }
    raise ValueError(f"未知工具: {name}")

async def main():
    """启动服务器"""
    # 通过stdio运行（MCP标准方式）
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await server.run(
                session,
                initializtion_options={}
            )

if __name__ == "__main__":
    asyncio.run(main())