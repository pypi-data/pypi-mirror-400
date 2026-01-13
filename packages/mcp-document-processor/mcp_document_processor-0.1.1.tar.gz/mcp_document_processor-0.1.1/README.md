# mcp-document-processor

一个简单的 MCP 服务器，提供 文档生成 功能。

## 功能
- 提供 `file_generate` 工具
- 支持自定义名称参数

## 构建包
python3 -m build

## 检查包
twine check dist/*

# 上传到测试PyPI
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# 上传到正式PyPI
twine upload dist/*

# PyPI API token
pypi-AgEIcHlwaS5vcmcCJDk1NmUxZmM4LTg4MDItNGU3Yy1hYWRhLWYzYjg3YTIwMzM2YwACKlszLCJlMzliYjBjOS1mM2Y0LTQ2YjQtODgwMS02YjdjYmQ1MDc3NGUiXQAABiDLJb7suhPf0uFa7XaWKFi4g3LWw5qJrMYwMjjfOEbnUw

## 备注
docker build -t registry.cn-beijing.aliyuncs.com/dev_base/frame:mcp-py-base-0.0.1 .

docker run -it --name=mcp_document_processor -p 8003:8003 xxx