import asyncio
from mcp.server import Server
import mcp.types as types

server = Server("document-processor-server")

@server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="hello",
            description="Returns a hello message in Chinese",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "hello":
        return types.CallToolResult(
            content=[types.TextContent(type="text", text="你好")]
        )

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
