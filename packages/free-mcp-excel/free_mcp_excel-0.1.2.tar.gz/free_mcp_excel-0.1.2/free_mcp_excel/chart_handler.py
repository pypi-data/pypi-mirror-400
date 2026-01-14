"""
图表处理类
提供Excel图表操作功能
"""
import io
from typing import Dict, Any, Optional

import openpyxl
from openpyxl.chart import BarChart, LineChart, PieChart, ScatterChart, AreaChart

from .utils import (
    base64_to_excel,
    detect_file_format,
    validate_file_size,
    format_error_response,
    format_success_response,
    parse_range_address,
    validate_range_address,
)
from .parser import ExcelParser


class ChartHandler:
    """图表处理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化图表处理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {
            "supported_types": ["bar", "line", "pie", "scatter", "area"]
        }
        self.parser = ExcelParser()
    
    def read_chart_info(
        self,
        file_base64: str,
        sheet: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        读取图表信息
        
        Args:
            file_base64: Excel文件的Base64编码
            sheet: 工作表名称，可选
            
        Returns:
            包含图表信息的响应字典
        """
        # 使用parser的方法
        return self.parser.read_chart_info(file_base64, sheet)
    
    def create_chart(
        self,
        file_base64: str,
        sheet: str,
        chart_type: str,
        data_range: str,
        title: Optional[str] = None,
        position: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        创建图表
        
        Args:
            file_base64: Excel文件的Base64编码
            sheet: 工作表名称
            chart_type: 图表类型
            data_range: 数据源范围
            title: 图表标题
            position: 图表位置
            
        Returns:
            包含更新后文件的响应字典
        """
        from .writer import ExcelWriter
        writer = ExcelWriter()
        return writer.create_chart(file_base64, sheet, chart_type, data_range, title, position)
    
    def update_chart(
        self,
        file_base64: str,
        sheet: str,
        chart_id: str,
        chart_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        更新图表
        
        Args:
            file_base64: Excel文件的Base64编码
            sheet: 工作表名称
            chart_id: 图表ID
            chart_config: 图表配置
            
        Returns:
            包含更新后文件的响应字典
        """
        from .writer import ExcelWriter
        writer = ExcelWriter()
        return writer.update_chart(file_base64, sheet, chart_id, chart_config)
    
    def delete_chart(
        self,
        file_base64: str,
        sheet: str,
        chart_id: str
    ) -> Dict[str, Any]:
        """
        删除图表
        
        Args:
            file_base64: Excel文件的Base64编码
            sheet: 工作表名称
            chart_id: 图表ID
            
        Returns:
            包含更新后文件的响应字典
        """
        from .writer import ExcelWriter
        writer = ExcelWriter()
        return writer.delete_chart(file_base64, sheet, chart_id)
    
    def _parse_chart_data(
        self,
        workbook,
        sheet,
        data_range: str
    ) -> Dict[str, Any]:
        """
        解析图表数据源
        
        Args:
            workbook: 工作簿对象
            sheet: 工作表对象
            data_range: 数据范围
            
        Returns:
            数据源信息
        """
        try:
            (start_row, start_col), (end_row, end_col) = parse_range_address(data_range)
            return {
                "start_row": start_row + 1,
                "start_col": start_col + 1,
                "end_row": end_row + 1 if end_row is not None else None,
                "end_col": end_col + 1 if end_col is not None else None
            }
        except Exception as e:
            return {"error": str(e)}

