"""
select_sheet_rows_by_id 工具 - 获取 sheet 的某一行数据
"""
from fastmcp import FastMCP
from uvx_excel_read_dbmod.base_mod.excel_manager import ExcelManager
from typing import Literal


def register_tool(mcp: FastMCP):
    """注册工具到 MCP 服务器"""

    @mcp.tool()
    def select_sheet_rows_by_id(
        file_path: str,
        sheet_name: str,
        row_id: int,
        engine: Literal["pandas", "polars"] = "pandas",
        header_row: int = 0
    ) -> dict:
        """
        根据 ID（行号）获取 sheet 中的某一行数据

        Args:
            file_path: Excel 文件路径
            sheet_name: sheet 名称
            row_id: 行号（从 1 开始，0 为表头）
            engine: 数据处理引擎，"pandas" 或 "polars"，默认 "pandas"
            header_row: 表头所在的行号（从 0 开始），默认 0

        Returns:
            包含行数据的字典：
            {
                "row_id": 行号,
                "data": {"字段名": "值", ...}
            }
        """
        try:
            manager = ExcelManager(file_path, engine=engine, header_row=header_row)
            data = manager.get_row_by_id(sheet_name, row_id)

            return {
                "row_id": row_id,
                "data": data
            }
        except ValueError as e:
            return {
                "error": str(e),
                "row_id": row_id,
                "data": {}
            }
        except Exception as e:
            return {
                "error": f"读取失败: {str(e)}",
                "row_id": row_id,
                "data": {}
            }
