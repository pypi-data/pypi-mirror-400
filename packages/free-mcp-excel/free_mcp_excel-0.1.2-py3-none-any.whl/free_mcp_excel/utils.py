"""
工具函数模块
提供Base64编码/解码、文件格式检测、文件大小校验等工具函数
"""
import base64
import io
from typing import Tuple, Optional, Dict, Any


# 文件格式签名
XLSX_SIGNATURE = b"PK\x03\x04"
XLS_SIGNATURE = b"\xD0\xCF\x11\xE0"

# 配置常量
MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def excel_to_base64(file_path: str) -> str:
    """
    将Excel文件转换为Base64编码字符串
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        Base64编码的字符串
        
    Raises:
        FileNotFoundError: 文件不存在
        IOError: 文件读取错误
    """
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
        return base64.b64encode(file_content).decode("utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在: {file_path}")
    except IOError as e:
        raise IOError(f"文件读取错误: {str(e)}")


def base64_to_excel(file_base64: str) -> bytes:
    """
    将Base64编码字符串转换为Excel文件二进制数据
    
    Args:
        file_base64: Base64编码的字符串
        
    Returns:
        Excel文件二进制数据
        
    Raises:
        ValueError: Base64解码失败
    """
    try:
        return base64.b64decode(file_base64)
    except Exception as e:
        raise ValueError(f"Base64解码失败: {str(e)}")


def detect_file_format(file_content: bytes) -> str:
    """
    检测Excel文件格式
    
    Args:
        file_content: 文件二进制数据
        
    Returns:
        文件格式：".xlsx" 或 ".xls"，如果不支持则返回空字符串
    """
    if file_content.startswith(XLSX_SIGNATURE):
        return ".xlsx"
    elif file_content.startswith(XLS_SIGNATURE):
        return ".xls"
    return ""


def validate_file_size(file_content: bytes) -> Tuple[bool, Optional[str]]:
    """
    验证文件大小
    
    Args:
        file_content: 文件二进制数据
        
    Returns:
        (是否有效, 错误信息)
    """
    file_size = len(file_content)
    file_size_mb = file_size / 1024 / 1024
    
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f"文件超过限制：最大支持{MAX_FILE_SIZE_MB}MB，当前文件{file_size_mb:.2f}MB"
    
    return True, None


def format_error_response(
    message: str,
    code: str = "ERROR",
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    格式化错误响应
    
    Args:
        message: 错误消息
        code: 错误代码
        details: 错误详情
        
    Returns:
        格式化的错误响应字典
    """
    error = {
        "message": message,
        "code": code
    }
    if details:
        error["details"] = details
    
    return {
        "status": "error",
        "error": error
    }


def format_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化成功响应
    
    Args:
        data: 响应数据
        
    Returns:
        格式化的成功响应字典
    """
    return {
        "status": "success",
        "data": data
    }


def parse_cell_address(cell: str) -> Tuple[int, int]:
    """
    解析单元格地址为行列索引（0-based）
    
    Args:
        cell: 单元格地址，如 "A1", "B2"
        
    Returns:
        (行索引, 列索引)
        
    Raises:
        ValueError: 地址格式错误
        
    Example:
        >>> parse_cell_address("A1")
        (0, 0)
        >>> parse_cell_address("B2")
        (1, 1)
    """
    import re
    
    # 匹配A1格式
    pattern = r"^([A-Z]+)(\d+)$"
    match = re.match(pattern, cell.upper())
    
    if not match:
        raise ValueError(f"无效的单元格地址格式: {cell}")
    
    col_str = match.group(1)
    row_str = match.group(2)
    
    # 转换列字母为数字（A=0, B=1, ..., Z=25, AA=26, ...）
    col = 0
    for char in col_str:
        col = col * 26 + (ord(char) - ord('A') + 1)
    col -= 1  # 转换为0-based
    
    # 转换行号为数字（1-based转0-based）
    row = int(row_str) - 1
    
    return row, col


def parse_range_address(range_str: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    解析范围地址为起始和结束行列索引
    
    Args:
        range_str: 范围地址，如 "A1:B10", "A:A"（整列）, "1:1"（整行）
        
    Returns:
        ((起始行, 起始列), (结束行, 结束列))
        
    Raises:
        ValueError: 地址格式错误
    """
    import re
    
    # 处理整列格式 A:A
    if re.match(r"^[A-Z]+:[A-Z]+$", range_str.upper()):
        col_match = re.match(r"^([A-Z]+):([A-Z]+)$", range_str.upper())
        if col_match:
            start_col_str = col_match.group(1)
            end_col_str = col_match.group(2)
            
            # 转换列字母
            start_col = 0
            for char in start_col_str:
                start_col = start_col * 26 + (ord(char) - ord('A') + 1)
            start_col -= 1
            
            end_col = 0
            for char in end_col_str:
                end_col = end_col * 26 + (ord(char) - ord('A') + 1)
            end_col -= 1
            
            # 整列：行从0到最大行（使用None表示）
            return ((0, start_col), (None, end_col))
    
    # 处理整行格式 1:1
    if re.match(r"^\d+:\d+$", range_str):
        row_match = re.match(r"^(\d+):(\d+)$", range_str)
        if row_match:
            start_row = int(row_match.group(1)) - 1
            end_row = int(row_match.group(2)) - 1
            # 整行：列从0到最大列（使用None表示）
            return ((start_row, 0), (end_row, None))
    
    # 处理标准范围格式 A1:B10
    pattern = r"^([A-Z]+\d+):([A-Z]+\d+)$"
    match = re.match(pattern, range_str.upper())
    
    if not match:
        raise ValueError(f"无效的范围地址格式: {range_str}")
    
    start_cell = match.group(1)
    end_cell = match.group(2)
    
    start_row, start_col = parse_cell_address(start_cell)
    end_row, end_col = parse_cell_address(end_cell)
    
    return ((start_row, start_col), (end_row, end_col))


def validate_cell_address(cell: str) -> bool:
    """
    验证单元格地址格式
    
    Args:
        cell: 单元格地址
        
    Returns:
        是否有效
    """
    import re
    pattern = r"^[A-Z]+\d+$"
    return bool(re.match(pattern, cell.upper()))


def validate_range_address(range_str: str) -> bool:
    """
    验证范围地址格式
    
    Args:
        range_str: 范围地址
        
    Returns:
        是否有效
    """
    import re
    
    # 支持格式：A1:B10, A:A, 1:1
    patterns = [
        r"^[A-Z]+\d+:[A-Z]+\d+$",  # A1:B10
        r"^[A-Z]+:[A-Z]+$",         # A:A
        r"^\d+:\d+$"                # 1:1
    ]
    
    for pattern in patterns:
        if re.match(pattern, range_str.upper()):
            return True
    
    return False


def get_column_letter(col_idx: int) -> str:
    """
    将列索引转换为列字母（1-based转字母）
    
    Args:
        col_idx: 列索引（1-based，A=1, B=2, ...）
        
    Returns:
        列字母，如 "A", "B", "AA"
    """
    result = ""
    while col_idx > 0:
        col_idx -= 1
        result = chr(ord('A') + (col_idx % 26)) + result
        col_idx //= 26
    return result


def get_column_index(col_letter: str) -> int:
    """
    将列字母转换为列索引（字母转1-based）
    
    Args:
        col_letter: 列字母，如 "A", "B", "AA"
        
    Returns:
        列索引（1-based，A=1, B=2, ...）
    """
    col_letter = col_letter.upper()
    result = 0
    for char in col_letter:
        result = result * 26 + (ord(char) - ord('A') + 1)
    return result

