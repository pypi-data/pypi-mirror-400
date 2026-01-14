"""
query_by_sql 工具 - 使用 SQL 语句查询 sheet 数据
"""
from fastmcp import FastMCP
from uvx_excel_read_dbmod.base_mod.excel_manager import ExcelManager
from typing import Literal


def register_tool(mcp: FastMCP):
    """注册工具到 MCP 服务器"""

    @mcp.tool()
    def query_by_sql(
        file_path: str,
        sheet_name: str,
        sql_query: str,
        table_name: str = "excel_table",
        engine: Literal["pandas", "polars"] = "polars",
        header_row: int = 0
    ) -> dict:
        """
        使用 SQL 语句查询 sheet 数据

        Args:
            file_path: Excel 文件路径
            sheet_name: sheet 名称
            sql_query: SQL 查询语句，支持完整的 SQL 语法（SELECT、WHERE、GROUP BY、ORDER BY、HAVING、LIMIT 等）
            table_name: 注册到 SQLContext 的表名，默认 "excel_table"。SQL 查询中应使用此表名
            engine: 数据处理引擎，"pandas" 或 "polars"，默认 "polars"（SQL 查询仅支持 polars）
            header_row: 表头所在的行号（从 0 开始），默认 0

        Returns:
            {
                "sheet_name": "sheet名称",
                "sql_query": "执行的SQL语句",
                "row_count": 返回的行数,
                "result": [{"字段1": "值1", "字段2": "值2", ...}, ...]
            }

        Example:
            query_by_sql(
                file_path="data.xlsx",
                sheet_name="Sheet1",
                sql_query="SELECT 来源, COUNT(*) AS 数量 FROM excel_table WHERE 来源 LIKE '%微信%' GROUP BY 来源"
            )
        """
        try:
            manager = ExcelManager(file_path, engine=engine, header_row=header_row)
            result = manager.query_by_sql(sheet_name, sql_query, table_name)

            if "error" in result:
                return result

            return {
                "sheet_name": sheet_name,
                "sql_query": sql_query,
                "row_count": result["row_count"],
                "result": result["result"]
            }
        except ValueError as e:
            return {
                "error": str(e),
                "sheet_name": sheet_name,
                "sql_query": sql_query,
                "row_count": 0,
                "result": []
            }
        except Exception as e:
            return {
                "error": f"SQL 查询失败: {str(e)}",
                "sheet_name": sheet_name,
                "sql_query": sql_query,
                "row_count": 0,
                "result": []
            }
