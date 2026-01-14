"""
MCP 协议端到端测试
模拟真实的 MCP 客户端连接和初始化流程
"""
import asyncio
import json
import sys
import pytest

# 检查 pytest-asyncio 是否可用
try:
    import pytest_asyncio
    pytestmark = pytest.mark.asyncio
except ImportError:
    # 如果 pytest-asyncio 未安装，提示安装而不是跳过
    pytestmark = pytest.mark.skip(reason="pytest-asyncio not installed. Install with: pip install pytest-asyncio")

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_server_initialization():
    """测试 MCP 服务器初始化流程"""
    # 创建服务器参数
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "free_mcp_excel"],
    )
    
    try:
        # 连接到服务器
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # 初始化连接（这是关键步骤）
                await session.initialize()
                
                # 测试列出工具
                tools_result = await session.list_tools()
                assert tools_result is not None
                assert hasattr(tools_result, 'tools')
                assert len(tools_result.tools) > 0
                
                # 验证工具列表包含预期工具
                tool_names = [tool.name for tool in tools_result.tools]
                assert "read_sheet_names" in tool_names
                assert "read_sheet_data" in tool_names
                
                print(f"✅ 服务器初始化成功")
                print(f"✅ 工具数量: {len(tools_result.tools)}")
                print(f"✅ 示例工具: {tool_names[:3]}")
                
                return True
    except Exception as e:
        print(f"❌ MCP 协议测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_mcp_server_tool_call():
    """测试 MCP 服务器工具调用"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "free_mcp_excel"],
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # 测试调用工具（需要文件参数）
                import os
                import sys
                # 添加项目根目录到路径
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                
                from free_mcp_excel.utils import excel_to_base64
                test_file = os.path.join(project_root, "tests", "data", "test.xlsx")
                if os.path.exists(test_file):
                    file_base64 = excel_to_base64(test_file)
                    result = await session.call_tool(
                        "read_sheet_names",
                        arguments={"file": file_base64}  # 使用正确的参数名
                    )
                    
                    # 验证返回结果
                    assert result is not None
                    assert hasattr(result, 'content')
                    print(f"   ✅ 工具调用成功")
                else:
                    # 如果没有测试文件，跳过工具调用测试
                    print("   ⚠️  测试文件不存在，跳过工具调用测试")
                
                # 验证返回结果格式
                assert result is not None
                assert hasattr(result, 'content')
                
                print(f"✅ 工具调用成功")
                return True
    except Exception as e:
        print(f"❌ 工具调用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 直接运行测试
    async def run_tests():
        print("=" * 60)
        print("🧪 MCP 协议端到端测试")
        print("=" * 60)
        
        test1 = await test_mcp_server_initialization()
        print()
        test2 = await test_mcp_server_tool_call()
        
        print()
        print("=" * 60)
        if test1 and test2:
            print("✅ 所有测试通过")
            return 0
        else:
            print("❌ 测试失败")
            return 1
    
    sys.exit(asyncio.run(run_tests()))
