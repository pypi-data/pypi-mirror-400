from .server import mcp

def main():
    """MCP Server - HTTP call API for MCP"""
    mcp.run()

if __name__ == "__main__":
    main()