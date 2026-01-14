"""
advanced_group_by 工具 - 高级分组统计，支持多字段分组和多种聚合函数
"""
from fastmcp import FastMCP
from uvx_excel_read_dbmod.base_mod.excel_manager import ExcelManager
from typing import Literal, Optional, List


def register_tool(mcp: FastMCP):
    """注册工具到 MCP 服务器"""

    @mcp.tool()
    def advanced_group_by(
        file_path: str,
        sheet_name: str,
        group_by_fields: List[str],
        aggregations: dict,
        engine: Literal["pandas", "polars"] = "pandas",
        header_row: int = 0,
        offset: int = 0,
        limit: Optional[int] = None,
        date_fields: Optional[List[str]] = None
    ) -> dict:
        """
        高级分组统计 - 支持多字段分组和多种聚合函数

        Args:
            file_path: Excel 文件路径
            sheet_name: sheet 名称
            group_by_fields: 分组字段列表（支持多个字段）
            aggregations: 聚合配置字典，格式：{字段名: [聚合函数列表]}
                          聚合函数支持: count, sum, mean, min, max, median, std
            engine: 数据处理引擎，"pandas" 或 "polars"，默认 "pandas"
            header_row: 表头所在的行号（从 0 开始），默认 0
            offset: 跳过前 N 条结果，用于分页，默认 0
            limit: 返回结果的最大数量，用于分页，默认 None（返回全部）
            date_fields: 需要解析为日期的字段列表，例如 ["日期", "创建时间"]

        Returns:
            {
                "sheet_name": "sheet名称",
                "group_by_fields": ["字段1", "字段2", ...],
                "aggregations": {"字段名": ["函数1", "函数2", ...], ...},
                "result_count": 当前返回的结果数量,
                "total_count": 总结果数量（分页前）,
                "offset": 跳过的数量,
                "limit": 限制的数量,
                "result": [
                    {
                        "分组字段1": "值1",
                        "分组字段2": "值2",
                        "聚合字段1_函数1": 值,
                        "聚合字段1_函数2": 值,
                        ...
                    },
                    ...
                ]
            }

        Example:
            按 "来源" 和 "完成情况" 分组，统计数量和提醒的平均值、总和、最大值:
            aggregations = {
                "提醒": ["count", "mean", "sum", "max"]
            }

            分页示例（每页 10 条，获取第 2 页）:
            offset = 10
            limit = 10

            日期字段示例（将"日期"字段解析为日期类型）:
            date_fields = ["日期"]
        """
        try:
            manager = ExcelManager(file_path, engine=engine, header_row=header_row)
            result = manager.advanced_group_by(sheet_name, group_by_fields, aggregations, offset, limit, date_fields)

            return result
        except ValueError as e:
            return {
                "error": str(e),
                "sheet_name": sheet_name,
                "group_by_fields": group_by_fields,
                "aggregations": aggregations,
                "result_count": 0,
                "total_count": 0,
                "result": [],
                "offset": offset,
                "limit": limit
            }
        except Exception as e:
            return {
                "error": f"高级分组统计失败: {str(e)}",
                "sheet_name": sheet_name,
                "group_by_fields": group_by_fields,
                "aggregations": aggregations,
                "result_count": 0,
                "total_count": 0,
                "result": [],
                "offset": offset,
                "limit": limit
            }
