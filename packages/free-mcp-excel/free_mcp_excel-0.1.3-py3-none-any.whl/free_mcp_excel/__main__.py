"""
模块入口，支持 python -m free_mcp_excel 运行
"""
from .server import main
import asyncio


def entry_point():
    """命令行入口点（同步函数）"""
    asyncio.run(main())


if __name__ == "__main__":
    entry_point()

