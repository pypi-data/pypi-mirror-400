import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 配置服务器参数，运行 MCP 服务器
    server_params = StdioServerParameters(
        command="python",
        args=["src/server.py"]
    )

    # 连接到服务器
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 初始化会话
            await session.initialize()

            # 列出可用工具
            tools = await session.list_tools()
            print("可用工具:", tools)

            # 调用工具
            result = await session.call_tool("file_generate", {"name": "测试文档"})
            print("工具调用结果:", result)

if __name__ == "__main__":
    asyncio.run(main())