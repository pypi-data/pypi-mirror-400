"""
集成测试用例
"""
import pytest
import base64
import openpyxl
import io
from free_mcp_excel.parser import ExcelParser
from free_mcp_excel.writer import ExcelWriter
from tests.conftest import load_test_file


@pytest.fixture
def parser():
    return ExcelParser()


@pytest.fixture
def writer():
    return ExcelWriter()


class TestIntegration:
    """集成测试类"""
    
    def test_e2e_create_and_read(self, writer, parser):
        """端到端测试：创建文件并读取"""
        # 1. 创建工作簿
        result1 = writer.create_workbook("TestSheet")
        assert result1["status"] == "success"
        file_base64 = result1["data"]["file"]
        
        # 2. 写入数据
        result2 = writer.write_range_data(
            file_base64,
            "TestSheet",
            "A1",
            [["列1", "列2"], ["值1", "值2"]]
        )
        assert result2["status"] == "success"
        file_base64 = result2["data"]["file"]
        
        # 3. 读取数据
        result3 = parser.read_sheet_data(file_base64, "TestSheet")
        assert result3["status"] == "success"
        assert len(result3["data"]["headers"]) == 2
        assert len(result3["data"]["data_rows"]) == 1
    
    def test_e2e_read_modify_save(self, parser, writer):
        """端到端测试：读取、修改、保存"""
        # 创建初始文件
        wb = openpyxl.Workbook()
        ws = wb.active
        ws["A1"] = "原始值"
        
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        file_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        wb.close()
        
        # 1. 读取
        result1 = parser.read_cell_data(file_base64, "Sheet", "A1")
        assert result1["status"] == "success"
        assert result1["data"]["cells"][0]["value"] == "原始值"
        
        # 2. 修改
        result2 = writer.write_cell_data(file_base64, "Sheet", "A1", "修改值")
        assert result2["status"] == "success"
        file_base64 = result2["data"]["file"]
        
        # 3. 验证修改
        result3 = parser.read_cell_data(file_base64, "Sheet", "A1")
        assert result3["status"] == "success"
        assert result3["data"]["cells"][0]["value"] == "修改值"
    
    def test_e2e_real_file_operations(self, parser, writer, test_file_xlsx_base64):
        """端到端测试：使用真实测试文件进行操作"""
        if not test_file_xlsx_base64:
            pytest.skip("测试文件不存在，跳过此测试")
        
        # 1. 读取真实文件的工作表名称
        result1 = parser.read_sheet_names(test_file_xlsx_base64)
        assert result1["status"] == "success"
        assert len(result1["data"]["sheet_names"]) > 0
        
        # 2. 读取第一个工作表的数据
        first_sheet = result1["data"]["sheet_names"][0]
        result2 = parser.read_sheet_data(test_file_xlsx_base64, sheet=first_sheet)
        assert result2["status"] == "success"
        
        # 3. 读取特定单元格
        result3 = parser.read_cell_data(test_file_xlsx_base64, first_sheet, "A1")
        assert result3["status"] == "success"
        
        # 4. 修改文件（添加新数据）
        result4 = writer.write_cell_data(
            test_file_xlsx_base64,
            first_sheet,
            "Z1",
            "测试数据"
        )
        assert result4["status"] == "success"
        
        # 5. 验证修改
        result5 = parser.read_cell_data(
            result4["data"]["file"],
            first_sheet,
            "Z1"
        )
        assert result5["status"] == "success"
        assert result5["data"]["cells"][0]["value"] == "测试数据"
    
    def test_e2e_complex_workflow(self, parser, writer, test_file_xlsx_base64):
        """端到端测试：复杂工作流（读取、分析、修改、保存）"""
        if not test_file_xlsx_base64:
            pytest.skip("测试文件不存在，跳过此测试")
        
        # 1. 获取工作簿信息
        info_result = parser.get_workbook_info(test_file_xlsx_base64)
        assert info_result["status"] == "success"
        
        # 2. 读取所有工作表
        sheets_result = parser.read_sheet_names(test_file_xlsx_base64)
        assert sheets_result["status"] == "success"
        
        # 3. 对每个工作表进行读取测试
        for sheet_name in sheets_result["data"]["sheet_names"][:3]:  # 只测试前3个工作表
            data_result = parser.read_sheet_data(
                test_file_xlsx_base64,
                sheet=sheet_name,
                skip_empty_rows=True
            )
            assert data_result["status"] == "success"
            
            # 如果工作表有数据，测试读取特定范围
            if data_result["data"]["row_count"] > 0:
                range_result = parser.read_sheet_data(
                    test_file_xlsx_base64,
                    sheet=sheet_name,
                    range="A1:B5"
                )
                assert range_result["status"] == "success"

