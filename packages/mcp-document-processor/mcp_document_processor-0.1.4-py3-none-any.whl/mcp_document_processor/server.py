import os
# import copy
import httpx
# from asyncio import sleep
 
from mcp.server.fastmcp import FastMCP
import mcp.types as types
import re
 
# 创建MCP服务器实例
mcp = FastMCP(
    name="mcp-document-processor",
    instructions="This is a MCP server for document processor."
)

api_key = os.getenv('BAIDU_MAPS_API_KEY')
api_url = "https://api.map.baidu.com"

async def file_generate(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    和规范化发
    """
    try:
        tag = arguments.get("tag", "abc123")
        
        url = ""
        params = {
            "type": f"{tag}",
            "scope": 2,
            "from": "py_mcp",
        }
        
        # if is_china == "true":
        #     if location:
        #         url = f"{api_url}/place/v3/around"
        #         params["location"] = f"{location}"
        #         params["radius"] = f"{radius}"
        #     else:
        #         url = f"{api_url}/place/v3/region"
        #         params["region"] = f"{region}"
        # elif is_china == "false":
        #     url = f"{api_url}/place_abroad/v1/search"
        #     if location:
        #         params["location"] = f"{location}"
        #         params["radius"] = f"{radius}"
        #     else:
        #         params["region"] = f"{region}"
        # else:
        #     raise Exception("input `is_china` invaild, please reinput `is_china` with `true` or `false`")

 
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(url, params=params)
        #     response.raise_for_status()
        #     result = response.json()
 
        # if result.get("status") != 0:
        #     error_msg = result.get("message", "unknown error")
            
        #     raise Exception(f"API response error: {mask_api_key(error_msg)}")
 
        # return [types.TextContent(type="text", text=response.text)]
        return [types.TextContent(type="text", text=params["from"])]
 
    except httpx.HTTPError as e:
        raise Exception(f"HTTP request failed: {str(e)}") from e
    except KeyError as e:
        raise Exception(f"Failed to parse reponse: {str(e)}") from e


async def map_weather(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    冻干粉大概
    """
    try:
        url = "" # f"{api_url}/weather/v1/?"
        
        params = {
            "ak": f"{api_key}",
            "data_type": "all",
            "from": "py_mcp"
        }
        
        # if not location:
        #     params["district_id"] = f"{district_id}"
        # else:
        #     params["location"] = f"{location}"
 
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(url, params=params)
        #     response.raise_for_status()
        #     result = response.json()
 
        # if result.get("status") != 0:
        #     error_msg = result.get("message", "unknown error")
        #     raise Exception(f"API response error: {mask_api_key(error_msg)}")
 
        # return [types.TextContent(type="text", text=response.text)]
        return [types.TextContent(type="text", text=params["data_type"])]
 
    except httpx.HTTPError as e:
        raise Exception(f"HTTP request failed: {str(e)}") from e
    except KeyError as e:
        raise Exception(f"Failed to parse reponse: {str(e)}") from e


async def list_tools() -> list[types.Tool]:
    """
    列出所有可用的工具。
    
    Args:
        None.
    
    Returns:
        list (types.Tool): 包含了所有可用的工具, 每个工具都包含了名称、描述、输入schema三个属性.
    """
    return [
        types.Tool(
            name="file_generate",
            description="嘎嘎嘎."
                        "\n灌灌灌灌."
                        "\n哈哈哈.",
            inputSchema={
                "type": "object",
                "required": ["query"],
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "检索分类, 以中文字符输入, 如'美食', 多个分类用英文逗号隔开, 如'美食,购物'",
                    },
                    # "radius": {
                    #     "type": "integer",
                    #     "description": "圆形区域检索半径, 单位：米",
                    # },
                },
            }
        ),
        types.Tool(
            name="map_weather",
            description="究极进化很高发热天.",
            inputSchema={
                "type": "object",
                "required": [],
                "properties": {
                    # "district_id": {
                    #     "type": "string",
                    #     "description": "行政区划代码, 需保证为6位无符号整数",
                    # },
                },
            }
        )
    ]


async def dispatch(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    根据名称调度对应的工具函数, 并返回处理结果.
    
    Args:
        name (str): 工具函数的名称, 可选值为: "file_generate", "map_weather".
        arguments (dict): 传递给工具函数的参数字典, 包括必要和可选参数.
    
    Returns:
        list[types.TextContent | types.ImageContent | types.EmbeddedResource]: 返回一个列表, 包含文本内容、图片内容或嵌入资源类型的元素.
    
    Raises:
        ValueError: 如果提供了未知的工具名称.
    """
    
    match name:
        case "file_generate":
            return await file_generate(name, arguments)
        case "map_weather":
            return await map_weather(name, arguments)
        case _:
            raise ValueError(f"Unknown tool: {name}")


# 注册list_tools方法
mcp._mcp_server.list_tools()(list_tools)
# 注册dispatch方法
mcp._mcp_server.call_tool()(dispatch)
 
if __name__ == "__main__":
    mcp.run()