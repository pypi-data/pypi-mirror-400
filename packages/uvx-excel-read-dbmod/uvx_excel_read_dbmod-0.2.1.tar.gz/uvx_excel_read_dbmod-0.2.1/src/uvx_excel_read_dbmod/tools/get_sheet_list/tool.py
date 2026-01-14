"""
get_sheet_list 工具 - 获取所有 sheet 列表、名称
"""
from fastmcp import FastMCP
from uvx_excel_read_dbmod.base_mod.excel_manager import ExcelManager
from typing import Literal


def register_tool(mcp: FastMCP):
    """注册工具到 MCP 服务器"""

    @mcp.tool()
    def get_sheet_list(
        file_path: str,
        engine: Literal["pandas", "polars"] = "pandas"
    ) -> dict:
        """
        获取 Excel 文件中所有 sheet 的列表和名称

        Args:
            file_path: Excel 文件路径
            engine: 数据处理引擎，"pandas" 或 "polars"，默认 "pandas"

        Returns:
            包含 sheet 列表的字典：
            {
                "sheet_count": sheet 数量,
                "sheet_names": ["sheet1", "sheet2", ...]
            }
        """
        try:
            manager = ExcelManager(file_path, engine=engine)
            sheet_names = manager.get_sheet_names()

            return {
                "sheet_count": len(sheet_names),
                "sheet_names": sheet_names
            }
        except FileNotFoundError as e:
            return {
                "error": str(e),
                "sheet_count": 0,
                "sheet_names": []
            }
        except Exception as e:
            return {
                "error": f"读取文件失败: {str(e)}",
                "sheet_count": 0,
                "sheet_names": []
            }
