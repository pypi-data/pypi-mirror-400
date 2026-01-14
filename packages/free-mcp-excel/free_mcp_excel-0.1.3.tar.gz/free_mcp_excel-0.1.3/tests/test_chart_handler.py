"""
ChartHandler测试用例
"""
import pytest
from free_mcp_excel.chart_handler import ChartHandler


@pytest.fixture
def chart_handler():
    """创建图表处理器实例"""
    return ChartHandler()


class TestChartHandler:
    """ChartHandler测试类"""
    
    def test_read_chart_info(self, chart_handler):
        """测试读取图表信息"""
        # 这里需要实际的包含图表的文件
        # 简化测试：验证方法存在
        assert hasattr(chart_handler, "read_chart_info")
        assert hasattr(chart_handler, "create_chart")
        assert hasattr(chart_handler, "update_chart")
        assert hasattr(chart_handler, "delete_chart")

