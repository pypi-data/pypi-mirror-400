"""
YMS MCP Server - stdio 传输模式

使用标准输入输出（stdio）方式运行 MCP 服务器。
适用于本地开发和 Claude Desktop 的 stdio 配置。
"""

from main import mcp

def main():
    """YMS MCP Server stdio 模式入口函数"""
    # 使用 stdio 传输方式运行服务器
    # 所有工具已在 main.py 中定义并注册
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()