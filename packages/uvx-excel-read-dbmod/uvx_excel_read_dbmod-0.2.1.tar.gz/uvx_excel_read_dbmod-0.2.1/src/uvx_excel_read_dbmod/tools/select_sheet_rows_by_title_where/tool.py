"""
select_sheet_rows_by_title_where 工具 - 根据多个表头的条件获取 sheet 的某行数据
支持完全匹配、模糊匹配、正则匹配、大于小于、区间、包含、不包含
"""
from fastmcp import FastMCP
from uvx_excel_read_dbmod.base_mod.excel_manager import ExcelManager
from typing import Literal, List, Union, Optional


def register_tool(mcp: FastMCP):
    """注册工具到 MCP 服务器"""

    @mcp.tool()
    def select_sheet_rows_by_title_where(
        file_path: str,
        sheet_name: str,
        conditions: List[dict],
        match_type: Literal["exact", "contains", "regex", "gt", "lt", "gte", "lte", "in", "not_in"] = "exact",
        engine: Literal["pandas", "polars"] = "pandas",
        header_row: int = 0,
        date_fields: Optional[List[str]] = None
    ) -> dict:
        """
        根据多个表头的条件获取 sheet 中的行数据

        支持的匹配类型：
        - exact: 完全匹配（默认）
        - contains: 包含（模糊匹配）
        - regex: 正则匹配
        - gt: 大于
        - lt: 小于
        - gte: 大于等于
        - lte: 小于等于
        - in: 在列表中
        - not_in: 不在列表中

        Args:
            file_path: Excel 文件路径
            sheet_name: sheet 名称
            conditions: 条件列表，每个条件包含 field（字段名）和 value（值）
                       例如: [{"field": "姓名", "value": "张三"}, {"field": "年龄", "value": 25}]
            match_type: 匹配类型，默认 "exact"
            engine: 数据处理引擎，"pandas" 或 "polars"，默认 "pandas"
            header_row: 表头所在的行号（从 0 开始），默认 0
            date_fields: 需要解析为日期的字段列表，用于正确的日期比较
                       例如: ["日期", "创建时间"]

        Returns:
            包含匹配行数据的字典：
            {
                "sheet_name": "sheet名称",
                "match_type": "匹配类型",
                "row_count": 匹配的行数,
                "data": [{"字段名": "值", ...}, ...]
            }

        Example:
            # 查询日期大于等于 2025-01-01 的记录
            select_sheet_rows_by_title_where(
                conditions=[{"field": "日期", "value": "2025-01-01"}],
                match_type="gte",
                date_fields=["日期"]
            )
        """
        try:
            manager = ExcelManager(file_path, engine=engine, header_row=header_row)
            data = manager.query_by_conditions(sheet_name, conditions, match_type, date_fields)

            return {
                "sheet_name": sheet_name,
                "match_type": match_type,
                "row_count": len(data),
                "data": data
            }
        except ValueError as e:
            return {
                "error": str(e),
                "sheet_name": sheet_name,
                "match_type": match_type,
                "row_count": 0,
                "data": []
            }
        except Exception as e:
            return {
                "error": f"查询失败: {str(e)}",
                "sheet_name": sheet_name,
                "match_type": match_type,
                "row_count": 0,
                "data": []
            }
