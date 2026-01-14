"""
group_by_sheet_title_get_count_and_values 工具 - 对某个表头进行分组，统计内容、行数
"""
from fastmcp import FastMCP
from uvx_excel_read_dbmod.base_mod.excel_manager import ExcelManager
from typing import Literal


def register_tool(mcp: FastMCP):
    """注册工具到 MCP 服务器"""

    @mcp.tool()
    def group_by_sheet_title_get_count_and_values(
        file_path: str,
        sheet_name: str,
        title: str,
        count_only: bool = False,
        engine: Literal["pandas", "polars"] = "pandas",
        header_row: int = 0
    ) -> dict:
        """
        对某个表头进行分组统计

        Args:
            file_path: Excel 文件路径
            sheet_name: sheet 名称
            title: 表头（字段）名
            count_only: 是否只返回计数，如果为 True 则返回 {值: 计数} 格式
                        如果为 False 则返回 [{"value": 值, "count": 计数}, ...] 格式
            engine: 数据处理引擎，"pandas" 或 "polars"，默认 "pandas"
            header_row: 表头所在的行号（从 0 开始），默认 0

        Returns:
            包含分组统计结果的字典：
            如果 count_only=True:
            {
                "sheet_name": "sheet名称",
                "title": "表头名",
                "group_count": 分组数量,
                "result": {"值1": 计数1, "值2": 计数2, ...}
            }
            如果 count_only=False:
            {
                "sheet_name": "sheet名称",
                "title": "表头名",
                "group_count": 分组数量,
                "result": [{"value": "值1", "count": 计数1}, {"value": "值2", "count": 计数2}, ...]
            }
        """
        try:
            manager = ExcelManager(file_path, engine=engine, header_row=header_row)
            result = manager.group_by_title(sheet_name, title, count_only)

            if count_only:
                return {
                    "sheet_name": sheet_name,
                    "title": title,
                    "group_count": len(result),
                    "result": result
                }
            else:
                return {
                    "sheet_name": sheet_name,
                    "title": title,
                    "group_count": len(result),
                    "result": result
                }
        except ValueError as e:
            return {
                "error": str(e),
                "sheet_name": sheet_name,
                "title": title,
                "group_count": 0,
                "result": {} if count_only else []
            }
        except Exception as e:
            return {
                "error": f"分组统计失败: {str(e)}",
                "sheet_name": sheet_name,
                "title": title,
                "group_count": 0,
                "result": {} if count_only else []
            }
