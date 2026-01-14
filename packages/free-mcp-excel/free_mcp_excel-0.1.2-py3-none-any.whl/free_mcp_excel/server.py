"""
MCP服务器主入口
提供MCP协议接口，注册所有工具方法
"""
import sys
import json
import asyncio
from typing import Dict, Any

try:
    from mcp import types
    from mcp.server.lowlevel import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
except ImportError:
    print("错误：无法导入MCP SDK，请安装：pip install mcp", file=sys.stderr)
    sys.exit(1)

from .parser import ExcelParser
from .writer import ExcelWriter
from .calculator import FormulaCalculator
from .chart_handler import ChartHandler
from .utils import excel_to_base64, base64_to_excel

# 配置
INTERNAL_CONFIG = {
    "provider": {
        "name": "free-mcp-excel",
        "version": "0.1.2",
        "description": "本地Excel MCP服务，支持.xlsx/.xls解析、写入、计算和图表处理"
    },
    "runtime": {
        "max_file_size_mb": 100,
        "skip_empty_rows": True,
        "support_formats": [".xlsx", ".xls"]
    }
}

# 创建MCP服务器实例
app = Server(INTERNAL_CONFIG["provider"]["name"])

# 初始化业务类
excel_parser = ExcelParser(INTERNAL_CONFIG["runtime"])
excel_writer = ExcelWriter()
formula_calculator = FormulaCalculator()
chart_handler = ChartHandler()


# ========================
# 工具注册
# ========================

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """返回可用工具列表"""
    return [
        # 读取类工具
        types.Tool(
            name="read_sheet_names",
            description="读取工作簿中所有工作表的名称列表",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Excel文件的Base64编码内容"
                    }
                },
                "required": ["file"]
            }
        ),
        types.Tool(
            name="read_sheet_data",
            description="读取指定工作表的数据，支持范围、行列过滤",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称，可选，默认第一个"},
                    "range": {"type": "string", "description": "数据范围，可选，如A1:B10"},
                    "skip_empty_rows": {"type": "boolean", "description": "是否跳过空行，可选"},
                    "skip_empty_cols": {"type": "boolean", "description": "是否跳过空列，可选"}
                },
                "required": ["file"]
            }
        ),
        types.Tool(
            name="read_cell_data",
            description="读取单个或范围单元格数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "cell": {"type": "string", "description": "单元格地址或范围，如A1或A1:B10"}
                },
                "required": ["file", "sheet", "cell"]
            }
        ),
        types.Tool(
            name="read_cell_formula",
            description="读取单元格公式",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "cell": {"type": "string", "description": "单元格地址"}
                },
                "required": ["file", "sheet", "cell"]
            }
        ),
        types.Tool(
            name="read_merged_cells",
            description="读取合并单元格信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称，可选"}
                },
                "required": ["file"]
            }
        ),
        types.Tool(
            name="read_chart_info",
            description="读取图表信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称，可选"}
                },
                "required": ["file"]
            }
        ),
        types.Tool(
            name="read_table_info",
            description="读取表格信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称，可选"}
                },
                "required": ["file"]
            }
        ),
        types.Tool(
            name="get_workbook_info",
            description="获取工作簿基本信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"}
                },
                "required": ["file"]
            }
        ),
        # 写入类工具
        types.Tool(
            name="create_workbook",
            description="创建新工作簿",
            inputSchema={
                "type": "object",
                "properties": {
                    "sheet_name": {"type": "string", "description": "默认工作表名称，可选"}
                }
            }
        ),
        types.Tool(
            name="create_sheet",
            description="创建工作表",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet_name": {"type": "string", "description": "新工作表名称"},
                    "position": {"type": "integer", "description": "插入位置，可选"}
                },
                "required": ["file", "sheet_name"]
            }
        ),
        types.Tool(
            name="write_cell_data",
            description="写入单元格数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "cell": {"type": "string", "description": "单元格地址"},
                    "value": {"description": "数据值"},
                    "data_type": {"type": "string", "description": "数据类型：text, number, date, boolean，可选"}
                },
                "required": ["file", "sheet", "cell", "value"]
            }
        ),
        types.Tool(
            name="write_cell_formula",
            description="写入单元格公式",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "cell": {"type": "string", "description": "单元格地址"},
                    "formula": {"type": "string", "description": "公式文本（应以=开头）"}
                },
                "required": ["file", "sheet", "cell", "formula"]
            }
        ),
        types.Tool(
            name="write_range_data",
            description="批量写入范围数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "start_cell": {"type": "string", "description": "起始单元格地址"},
                    "data": {
                        "type": "array",
                        "items": {"type": "array"},
                        "description": "二维数据数组"
                    }
                },
                "required": ["file", "sheet", "start_cell", "data"]
            }
        ),
        types.Tool(
            name="merge_cells",
            description="合并单元格",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "range": {"type": "string", "description": "合并范围，如A1:B1"}
                },
                "required": ["file", "sheet", "range"]
            }
        ),
        types.Tool(
            name="unmerge_cells",
            description="取消合并单元格",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "range": {"type": "string", "description": "取消合并的范围"}
                },
                "required": ["file", "sheet", "range"]
            }
        ),
        types.Tool(
            name="create_chart",
            description="创建图表",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "chart_type": {"type": "string", "description": "图表类型：bar, line, pie, scatter, area"},
                    "data_range": {"type": "string", "description": "数据源范围"},
                    "title": {"type": "string", "description": "图表标题，可选"},
                    "position": {
                        "type": "object",
                        "description": "图表位置，可选，包含x, y, width, height"
                    }
                },
                "required": ["file", "sheet", "chart_type", "data_range"]
            }
        ),
        types.Tool(
            name="update_chart",
            description="更新图表",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "chart_id": {"type": "string", "description": "图表ID或名称"},
                    "chart_config": {"type": "object", "description": "图表配置"}
                },
                "required": ["file", "sheet", "chart_id", "chart_config"]
            }
        ),
        types.Tool(
            name="delete_chart",
            description="删除图表",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "chart_id": {"type": "string", "description": "图表ID或名称"}
                },
                "required": ["file", "sheet", "chart_id"]
            }
        ),
        types.Tool(
            name="create_table",
            description="创建表格",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "range": {"type": "string", "description": "表格范围"},
                    "table_style": {"type": "string", "description": "表格样式，可选"}
                },
                "required": ["file", "sheet", "range"]
            }
        ),
        types.Tool(
            name="save_workbook",
            description="保存工作簿",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "options": {"type": "object", "description": "保存选项，可选"}
                },
                "required": ["file"]
            }
        ),
        # 计算类工具
        types.Tool(
            name="calc_cell_data",
            description="计算单元格值（混合模式：优先读取已计算值，需要时使用公式引擎）",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "cell": {"type": "string", "description": "单元格地址"},
                    "force_recalc": {"type": "boolean", "description": "是否强制重新计算，可选"}
                },
                "required": ["file", "sheet", "cell"]
            }
        ),
        types.Tool(
            name="calc_range_data",
            description="计算范围数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Excel文件的Base64编码内容"},
                    "sheet": {"type": "string", "description": "工作表名称"},
                    "range": {"type": "string", "description": "单元格范围"}
                },
                "required": ["file", "sheet", "range"]
            }
        ),
        types.Tool(
            name="evaluate_formula",
            description="评估公式表达式",
            inputSchema={
                "type": "object",
                "properties": {
                    "formula": {"type": "string", "description": "公式文本"},
                    "context": {"type": "object", "description": "上下文数据（单元格值字典），可选"}
                },
                "required": ["formula"]
            }
        ),
        # 工具类工具
        types.Tool(
            name="excel_to_base64",
            description="Excel文件转Base64（用于测试，实际使用中文件已为Base64）",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Excel文件路径"}
                },
                "required": ["file_path"]
            }
        ),
        types.Tool(
            name="base64_to_excel",
            description="Base64转Excel文件（用于测试）",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_base64": {"type": "string", "description": "Base64编码字符串"},
                    "output_path": {"type": "string", "description": "输出文件路径"}
                },
                "required": ["file_base64", "output_path"]
            }
        ),
    ]


@app.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """处理工具调用"""
    try:
        result = None
        
        # 读取类工具
        if name == "read_sheet_names":
            result = excel_parser.read_sheet_names(arguments["file"])
        elif name == "read_sheet_data":
            result = excel_parser.read_sheet_data(
                arguments["file"],
                arguments.get("sheet"),
                arguments.get("range"),
                arguments.get("skip_empty_rows"),
                arguments.get("skip_empty_cols", False)
            )
        elif name == "read_cell_data":
            result = excel_parser.read_cell_data(
                arguments["file"],
                arguments["sheet"],
                arguments["cell"]
            )
        elif name == "read_cell_formula":
            result = excel_parser.read_cell_formula(
                arguments["file"],
                arguments["sheet"],
                arguments["cell"]
            )
        elif name == "read_merged_cells":
            result = excel_parser.read_merged_cells(
                arguments["file"],
                arguments.get("sheet")
            )
        elif name == "read_chart_info":
            result = excel_parser.read_chart_info(
                arguments["file"],
                arguments.get("sheet")
            )
        elif name == "read_table_info":
            result = excel_parser.read_table_info(
                arguments["file"],
                arguments.get("sheet")
            )
        elif name == "get_workbook_info":
            result = excel_parser.get_workbook_info(arguments["file"])
        
        # 写入类工具
        elif name == "create_workbook":
            result = excel_writer.create_workbook(arguments.get("sheet_name", "Sheet1"))
        elif name == "create_sheet":
            result = excel_writer.create_sheet(
                arguments["file"],
                arguments["sheet_name"],
                arguments.get("position")
            )
        elif name == "write_cell_data":
            result = excel_writer.write_cell_data(
                arguments["file"],
                arguments["sheet"],
                arguments["cell"],
                arguments["value"],
                arguments.get("data_type")
            )
        elif name == "write_cell_formula":
            result = excel_writer.write_cell_formula(
                arguments["file"],
                arguments["sheet"],
                arguments["cell"],
                arguments["formula"]
            )
        elif name == "write_range_data":
            result = excel_writer.write_range_data(
                arguments["file"],
                arguments["sheet"],
                arguments["start_cell"],
                arguments["data"]
            )
        elif name == "merge_cells":
            result = excel_writer.merge_cells(
                arguments["file"],
                arguments["sheet"],
                arguments["range"]
            )
        elif name == "unmerge_cells":
            result = excel_writer.unmerge_cells(
                arguments["file"],
                arguments["sheet"],
                arguments["range"]
            )
        elif name == "create_chart":
            result = chart_handler.create_chart(
                arguments["file"],
                arguments["sheet"],
                arguments["chart_type"],
                arguments["data_range"],
                arguments.get("title"),
                arguments.get("position")
            )
        elif name == "update_chart":
            result = chart_handler.update_chart(
                arguments["file"],
                arguments["sheet"],
                arguments["chart_id"],
                arguments["chart_config"]
            )
        elif name == "delete_chart":
            result = chart_handler.delete_chart(
                arguments["file"],
                arguments["sheet"],
                arguments["chart_id"]
            )
        elif name == "create_table":
            result = excel_writer.create_table(
                arguments["file"],
                arguments["sheet"],
                arguments["range"],
                arguments.get("table_style")
            )
        elif name == "save_workbook":
            result = excel_writer.save_workbook(
                arguments["file"],
                arguments.get("options")
            )
        
        # 计算类工具
        elif name == "calc_cell_data":
            result = formula_calculator.calc_cell_data(
                arguments["file"],
                arguments["sheet"],
                arguments["cell"],
                arguments.get("force_recalc", False)
            )
        elif name == "calc_range_data":
            result = formula_calculator.calc_range_data(
                arguments["file"],
                arguments["sheet"],
                arguments["range"]
            )  # 注意：这里arguments["range"]会传递给range_str参数
        elif name == "evaluate_formula":
            result = formula_calculator.evaluate_formula(
                arguments["formula"],
                arguments.get("context")
            )
        
        # 工具类工具
        elif name == "excel_to_base64":
            try:
                file_base64 = excel_to_base64(arguments["file_path"])
                result = {
                    "status": "success",
                    "data": {"file": file_base64}
                }
            except Exception as e:
                result = {
                    "status": "error",
                    "error": {"message": str(e), "code": "CONVERSION_ERROR"}
                }
        elif name == "base64_to_excel":
            try:
                file_content = base64_to_excel(arguments["file_base64"])
                with open(arguments["output_path"], "wb") as f:
                    f.write(file_content)
                result = {
                    "status": "success",
                    "data": {"output_path": arguments["output_path"]}
                }
            except Exception as e:
                result = {
                    "status": "error",
                    "error": {"message": str(e), "code": "CONVERSION_ERROR"}
                }
        else:
            result = {
                "status": "error",
                "error": {"message": f"不支持的工具：{name}", "code": "UNKNOWN_TOOL"}
            }
        
        # 格式化响应
        if result is None:
            result = {
                "status": "error",
                "error": {"message": "工具执行失败", "code": "EXECUTION_ERROR"}
            }
        
        return [types.TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False)
        )]
    except Exception as e:
        error_result = {
            "status": "error",
            "error": {
                "message": f"工具调用异常：{str(e)}",
                "code": "EXCEPTION"
            }
        }
        return [types.TextContent(
            type="text",
            text=json.dumps(error_result, ensure_ascii=False)
        )]


async def main():
    """
    MCP服务器主入口，通过stdio进行通信
    注意：所有日志输出必须写入stderr，避免干扰MCP协议通信
    """
    # 准备初始化选项（在启动前准备好，避免阻塞）
    init_options = InitializationOptions(
        server_name=INTERNAL_CONFIG["provider"]["name"],
        server_version=INTERNAL_CONFIG["provider"]["version"],
        capabilities=app.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={}
        )
    )
    
    # 启动日志（输出到stderr，在服务器运行前输出）
    print("=" * 60, file=sys.stderr)
    print(f"✅ 本地Excel MCP服务 [{INTERNAL_CONFIG['provider']['name']}] 启动成功", file=sys.stderr)
    print(f"🔧 支持格式：{','.join(INTERNAL_CONFIG['runtime']['support_formats'])}", file=sys.stderr)
    print(f"📌 运行模式：纯本地进程内（无端口、无网络依赖）", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    # 通过stdio运行MCP服务器
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            init_options
        )


if __name__ == "__main__":
    asyncio.run(main())

