"""
search_row_in_sheet_by_keyword 工具 - 在某个 sheet 中搜索某个关键字
"""
from fastmcp import FastMCP
from uvx_excel_read_dbmod.base_mod.excel_manager import ExcelManager
from typing import Literal


def register_tool(mcp: FastMCP):
    """注册工具到 MCP 服务器"""

    @mcp.tool()
    def search_row_in_sheet_by_keyword(
        file_path: str,
        sheet_name: str,
        keyword: str,
        case_sensitive: bool = False,
        engine: Literal["pandas", "polars"] = "pandas",
        header_row: int = 0
    ) -> dict:
        """
        在某个 sheet 中搜索包含某个关键字的所有行

        Args:
            file_path: Excel 文件路径
            sheet_name: sheet 名称
            keyword: 搜索关键字
            case_sensitive: 是否区分大小写，默认 False
            engine: 数据处理引擎，"pandas" 或 "polars"，默认 "pandas"
            header_row: 表头所在的行号（从 0 开始），默认 0

        Returns:
            包含搜索结果的字典：
            {
                "sheet_name": "sheet名称",
                "keyword": "搜索关键字",
                "match_count": 匹配的行数,
                "data": [
                    {"_row_id": 行号, "字段名1": "值1", ...},
                    ...
                ]
            }
        """
        try:
            manager = ExcelManager(file_path, engine=engine, header_row=header_row)
            data = manager.search_keyword(sheet_name, keyword, case_sensitive)

            return {
                "sheet_name": sheet_name,
                "keyword": keyword,
                "match_count": len(data),
                "data": data
            }
        except Exception as e:
            return {
                "error": f"搜索失败: {str(e)}",
                "sheet_name": sheet_name,
                "keyword": keyword,
                "match_count": 0,
                "data": []
            }
