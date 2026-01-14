from fastmcp import FastMCP
from typing import List, Optional, Any
import json
# 导入你的工具库
import utils 

# 1. 创建 MCP 服务
mcp = FastMCP("Excel Tools")

# --- 原有功能 ---

@mcp.tool()
def read_excel_sheet(file_path: str, sheet_name: str = None, limit: int = 100) -> str:
    """
    读取 Excel 文件中的数据。
    Args:
        file_path: Excel 文件的本地路径
        sheet_name: 工作表名称，如果不填则读取当前激活的表
        limit: 限制读取的行数，默认 100 行
    """
    try:
        data = utils.read_sheet(file_path, sheet=sheet_name, limit=limit)
        return json.dumps(data, ensure_ascii=False)
    except Exception as e:
        return f"读取失败: {str(e)}"

@mcp.tool()
def describe_workbook(file_path: str) -> str:
    """
    查看 Excel 文件里有哪些工作表，以及行数列数。
    """
    try:
        info = utils.describe_sheets(file_path)
        return json.dumps(info, ensure_ascii=False)
    except Exception as e:
        return f"获取信息失败: {str(e)}"

@mcp.tool()
def write_rows_to_excel(file_path: str, sheet_name: str, rows: List[List[Any]]) -> str:
    """
    追加写入数据。如果文件不存在会自动创建。
    rows 示例: [["张三", 18], ["李四", 20]]
    """
    try:
        utils.write_to_sheet(file_path, sheet_name, rows)
        return "写入成功"
    except Exception as e:
        return f"写入失败: {str(e)}"

@mcp.tool()
def create_new_table(file_path: str, sheet_name: str, header: List[str], rows: List[List[Any]]) -> str:
    """
    创建一个新表（包含表头）。
    """
    try:
        utils.create_table(file_path, sheet_name, header, rows)
        return "创建表格成功"
    except Exception as e:
        return f"创建失败: {str(e)}"

@mcp.tool()
def format_excel_range(file_path: str, sheet_name: str, start_cell: str, end_cell: str, is_bold: bool = False, bg_color: str = None, align_center: bool = False) -> str:
    """
    设置格式（加粗/背景色/居中）。
    Args:
        bg_color: 颜色代码如 '#FF0000'
        align_center: 是否居中对齐
    """
    try:
        utils.format_range(file_path, sheet_name, start_cell, end_cell, bold=is_bold, bg_hex=bg_color, align_center=align_center)
        return "格式设置成功"
    except Exception as e:
        return f"格式设置失败: {str(e)}"

# --- 新增的 5 个功能 ---

@mcp.tool()
def delete_worksheet(file_path: str, sheet_name: str) -> str:
    """
    【危险】删除指定的工作表。
    """
    try:
        utils.delete_sheet(file_path, sheet_name)
        return f"工作表 {sheet_name} 已删除"
    except Exception as e:
        return f"删除失败: {str(e)}"

@mcp.tool()
def merge_excel_cells(file_path: str, sheet_name: str, start_cell: str, end_cell: str) -> str:
    """
    合并单元格区域，例如 'A1' 到 'B2'。
    """
    try:
        utils.merge_cells(file_path, sheet_name, start_cell, end_cell)
        return "合并成功"
    except Exception as e:
        return f"合并失败: {str(e)}"

@mcp.tool()
def write_excel_formula(file_path: str, sheet_name: str, cell: str, formula: str) -> str:
    """
    写入公式。
    Args:
        cell: 单元格位置，如 'E10'
        formula: Excel公式，如 '=SUM(A1:A10)'
    """
    try:
        utils.write_formula(file_path, sheet_name, cell, formula)
        return "公式写入成功"
    except Exception as e:
        return f"公式写入失败: {str(e)}"

@mcp.tool()
def set_col_width(file_path: str, sheet_name: str, column: str, width: float) -> str:
    """
    设置列宽。
    Args:
        column: 列号，如 'A'
        width: 宽度数字，如 20
    """
    try:
        utils.set_column_width(file_path, sheet_name, column, width)
        return f"{column} 列宽已设置为 {width}"
    except Exception as e:
        return f"设置列宽失败: {str(e)}"

@mcp.tool()
def add_filter_to_range(file_path: str, sheet_name: str, cell_range: str) -> str:
    """
    给表格添加自动筛选（漏斗图标）。
    Args:
        cell_range: 区域，如 'A1:D1'
    """
    try:
        utils.add_auto_filter(file_path, sheet_name, cell_range)
        return "筛选添加成功"
    except Exception as e:
        return f"添加筛选失败: {str(e)}"

# 启动服务
if __name__ == "__main__":
    mcp.run()