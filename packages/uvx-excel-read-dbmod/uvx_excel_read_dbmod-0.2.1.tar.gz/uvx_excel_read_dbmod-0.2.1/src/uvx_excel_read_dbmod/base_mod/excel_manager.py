"""
Excel 文件管理器 - 支持 pandas 和 polars 两种数据处理方式
"""
from pathlib import Path
from typing import Optional, Literal, Union, List

from .pandas import PandasEngine
from .polars import PolarsEngine


class ExcelManager:
    """Excel 文件管理器，提供统一的访问接口"""

    def __init__(
        self,
        file_path: str,
        engine: Literal["pandas", "polars"] = "pandas",
        header_row: int = 0
    ):
        """
        初始化 Excel 管理器

        Args:
            file_path: Excel 文件路径
            engine: 数据处理引擎，支持 "pandas" 或 "polars"
            header_row: 表头所在的行号（从 0 开始），默认 0
        """
        self.file_path = Path(file_path)
        self.engine = engine
        self.header_row = header_row
        self._sheet_names: Optional[list[str]] = None

        # 根据引擎类型创建对应的引擎实例
        if engine == "pandas":
            self._engine = PandasEngine(file_path, header_row)
        else:
            self._engine = PolarsEngine(file_path, header_row)

    def get_sheet_names(self) -> list[str]:
        """获取所有 sheet 名称"""
        if self._sheet_names is None:
            self._sheet_names = self._engine.get_sheet_names()
        return self._sheet_names

    def get_sheet_title(self, sheet_name: str) -> list[str]:
        """
        获取 sheet 的表头（字段名）

        Args:
            sheet_name: sheet 名称

        Returns:
            表头列表
        """
        return self._engine.get_title(sheet_name)

    def get_row_count(self, sheet_name: str) -> int:
        """
        获取 sheet 的行数

        Args:
            sheet_name: sheet 名称

        Returns:
            行数
        """
        return self._engine.get_row_count(sheet_name)

    def get_row_by_id(self, sheet_name: str, row_id: int) -> dict:
        """
        根据 ID（行号）获取数据

        Args:
            sheet_name: sheet 名称
            row_id: 行号（从 1 开始，0 为表头）

        Returns:
            行数据字典 {字段名: 值}
        """
        if row_id < 1:
            raise ValueError("行号必须从 1 开始")
        return self._engine.get_row_by_id(sheet_name, row_id)

    def query_by_conditions(
        self,
        sheet_name: str,
        conditions: list[dict],
        match_type: Literal["exact", "contains", "regex", "gt", "lt", "gte", "lte", "in", "not_in"] = "exact",
        date_fields: list[str] = None
    ) -> list[dict]:
        """
        根据多个条件查询数据

        Args:
            sheet_name: sheet 名称
            conditions: 条件列表，每个条件包含 field（字段名）和 value（值）
            match_type: 匹配类型
                - exact: 完全匹配
                - contains: 包含
                - regex: 正则匹配
                - gt: 大于
                - lt: 小于
                - gte: 大于等于
                - lte: 小于等于
                - in: 在列表中
                - not_in: 不在列表中
            date_fields: 需要解析为日期的字段列表

        Returns:
            匹配的行数据列表
        """
        if date_fields is None:
            date_fields = []
        return self._engine.query_by_conditions(sheet_name, conditions, match_type, date_fields)

    def group_by_title(
        self,
        sheet_name: str,
        title: str,
        count_only: bool = False
    ) -> Union[dict, list[dict]]:
        """
        按表头分组统计

        Args:
            sheet_name: sheet 名称
            title: 表头（字段）名
            count_only: 是否只返回计数

        Returns:
            如果 count_only=True，返回 {值: 计数}
            否则返回 [{值: xxx, count: xxx}, ...]
        """
        return self._engine.group_by_title(sheet_name, title, count_only)

    def search_keyword(
        self,
        sheet_name: str,
        keyword: str,
        case_sensitive: bool = False
    ) -> list[dict]:
        """
        在 sheet 中搜索关键字

        Args:
            sheet_name: sheet 名称
            keyword: 搜索关键字
            case_sensitive: 是否区分大小写

        Returns:
            包含关键字的行数据列表（附带行号信息）
        """
        return self._engine.search_keyword(sheet_name, keyword, case_sensitive)

    def advanced_group_by(
        self,
        sheet_name: str,
        group_by_fields: list[str],
        aggregations: dict,
        offset: int = 0,
        limit: int = None,
        date_fields: list[str] = None
    ) -> dict:
        """
        高级分组统计 - 支持多字段分组和多种聚合函数

        Args:
            sheet_name: sheet 名称
            group_by_fields: 分组字段列表（支持多个字段）
            aggregations: 聚合配置字典，格式：{字段名: [聚合函数列表]}
                         聚合函数支持: count, sum, mean, min, max, median, std
            offset: 跳过前 N 条结果，用于分页，默认 0
            limit: 返回结果的最大数量，用于分页，默认 None（返回全部）
            date_fields: 需要解析为日期的字段列表

        Returns:
            {
                "sheet_name": str,
                "group_by_fields": list[str],
                "aggregations": dict,
                "result_count": int,
                "result": list[dict],
                "offset": int,
                "limit": int
            }
        """
        if date_fields is None:
            date_fields = []
        return self._engine.advanced_group_by(sheet_name, group_by_fields, aggregations, offset, limit, date_fields)

    def query_by_sql(
        self,
        sheet_name: str,
        sql_query: str,
        table_name: str = "excel_table"
    ) -> dict:
        """
        使用 SQL 语句查询数据（仅支持 polars 引擎）

        Args:
            sheet_name: sheet 名称
            sql_query: SQL 查询语句
            table_name: 注册到 SQLContext 的表名，默认 "excel_table"

        Returns:
            {
                "sheet_name": str,
                "sql_query": str,
                "row_count": int,
                "result": list[dict]
            }

        Note:
            此功能仅支持 polars 引擎。如果使用 pandas 引擎，
            将返回错误提示建议切换到 polars。
        """
        return self._engine.query_by_sql(sheet_name, sql_query, table_name)
