# mcp-document-processor

一个简单的 MCP 服务器，提供 文档生成 功能。

## 功能
- 提供 `file_generate` 工具
- 支持自定义名称参数

docker build -t registry.cn-beijing.aliyuncs.com/dev_base/frame:mcp-py-base-0.0.1 .

docker run -it --name=mcp_document_processor -p 8003:8003 xxx