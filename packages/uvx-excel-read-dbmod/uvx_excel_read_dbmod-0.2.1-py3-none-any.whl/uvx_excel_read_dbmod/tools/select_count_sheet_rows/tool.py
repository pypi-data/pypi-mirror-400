"""
select_count_sheet_rows 工具 - 获取 sheet 的行数
"""
from fastmcp import FastMCP
from uvx_excel_read_dbmod.base_mod.excel_manager import ExcelManager
from typing import Literal


def register_tool(mcp: FastMCP):
    """注册工具到 MCP 服务器"""

    @mcp.tool()
    def select_count_sheet_rows(
        file_path: str,
        sheet_name: str,
        engine: Literal["pandas", "polars"] = "pandas",
        header_row: int = 0
    ) -> dict:
        """
        获取指定 sheet 的行数

        Args:
            file_path: Excel 文件路径
            sheet_name: sheet 名称
            engine: 数据处理引擎，"pandas" 或 "polars"，默认 "pandas"
            header_row: 表头所在的行号（从 0 开始），默认 0

        Returns:
            包含行数的字典：
            {
                "sheet_name": "sheet名称",
                "row_count": 行数
            }
        """
        try:
            manager = ExcelManager(file_path, engine=engine, header_row=header_row)
            row_count = manager.get_row_count(sheet_name)

            return {
                "sheet_name": sheet_name,
                "row_count": row_count
            }
        except FileNotFoundError as e:
            return {
                "error": str(e),
                "sheet_name": sheet_name,
                "row_count": 0
            }
        except Exception as e:
            return {
                "error": f"读取失败: {str(e)}",
                "sheet_name": sheet_name,
                "row_count": 0
            }
