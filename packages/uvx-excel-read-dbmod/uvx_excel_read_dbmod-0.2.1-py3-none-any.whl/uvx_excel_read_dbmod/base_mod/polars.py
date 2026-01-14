"""
Polars 引擎 - 使用 polars 处理 Excel 文件
"""
import polars as pl
from pathlib import Path
from typing import Union, List


class PolarsEngine:
    """Polars 数据处理引擎"""

    def __init__(self, file_path: str, header_row: int = 0):
        """
        初始化 Polars 引擎

        Args:
            file_path: Excel 文件路径
            header_row: 表头所在的行号（从 0 开始），默认 0
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        self.header_row = header_row

    def get_sheet_names(self) -> list[str]:
        """获取所有 sheet 名称（需要使用 openpyxl）"""
        import openpyxl
        wb = openpyxl.load_workbook(self.file_path, read_only=True)
        return wb.sheetnames

    def get_title(self, sheet_name: str) -> list[str]:
        """获取 sheet 的表头（字段名）"""
        if self.header_row > 0:
            df = pl.read_excel(self.file_path, sheet_name=sheet_name, read_options={"skip_rows": self.header_row})
            return df.columns
        else:
            df = pl.read_excel(self.file_path, sheet_name=sheet_name)
            return df.columns

    def get_row_count(self, sheet_name: str) -> int:
        """获取 sheet 的行数"""
        if self.header_row > 0:
            df = pl.read_excel(self.file_path, sheet_name=sheet_name, read_options={"skip_rows": self.header_row})
        else:
            df = pl.read_excel(self.file_path, sheet_name=sheet_name)
        return len(df)

    def get_row_by_id(self, sheet_name: str, row_id: int) -> dict:
        """根据 ID（行号）获取数据"""
        df = pl.read_excel(self.file_path, sheet_name=sheet_name)
        if row_id > len(df):
            raise ValueError(f"行号 {row_id} 超出范围，总行数: {len(df)}")
        row = df.row(row_id - 1)
        return dict(zip(df.columns, row))

    def parse_date_fields(self, df: pl.DataFrame, date_fields: list[str]) -> pl.DataFrame:
        """
        将指定字段转换为日期类型

        Args:
            df: polars DataFrame
            date_fields: 需要转换为日期的字段列表

        Returns:
            转换后的 DataFrame
        """
        if not date_fields:
            return df

        for field in date_fields:
            if field in df.columns:
                df = df.with_columns(
                    pl.col(field).str.strptime(pl.Date, "%Y-%m-%d", strict=False)
                        .fill_null(
                            pl.col(field).str.strptime(pl.Date, "%Y/%m/%d", strict=False)
                        )
                        .fill_null(
                            pl.col(field).str.strptime(pl.Date, "%Y-%m-%d %H:%M:%S", strict=False)
                        )
                        .fill_null(
                            pl.col(field).str.strptime(pl.Date, "%Y/%m/%d %H:%M:%S", strict=False)
                        )
                        .alias(field)
                )

        return df

    def query_by_conditions(
        self,
        sheet_name: str,
        conditions: list[dict],
        match_type: str,
        date_fields: list[str] = None
    ) -> list[dict]:
        """根据多个条件查询数据"""
        if date_fields is None:
            date_fields = []

        df = pl.read_excel(self.file_path, sheet_name=sheet_name)

        # 处理日期字段
        if date_fields:
            df = self.parse_date_fields(df, date_fields)

        for condition in conditions:
            field = condition.get("field")
            value = condition.get("value")

            if field not in df.columns:
                raise ValueError(f"字段 '{field}' 不存在")

            if match_type == "exact":
                df = df.filter(pl.col(field) == value)
            elif match_type == "contains":
                df = df.filter(pl.col(field).cast(pl.Utf8).str.contains(str(value)))
            elif match_type == "regex":
                df = df.filter(pl.col(field).cast(pl.Utf8).str.contains(str(value)))
            elif match_type == "gt":
                df = df.filter(pl.col(field) > value)
            elif match_type == "lt":
                df = df.filter(pl.col(field) < value)
            elif match_type == "gte":
                df = df.filter(pl.col(field) >= value)
            elif match_type == "lte":
                df = df.filter(pl.col(field) <= value)
            elif match_type == "in":
                df = df.filter(pl.col(field).is_in(value))
            elif match_type == "not_in":
                df = df.filter(~pl.col(field).is_in(value))

        return df.to_dicts()

    def group_by_title(
        self,
        sheet_name: str,
        title: str,
        count_only: bool
    ) -> Union[dict, list[dict]]:
        """按表头分组统计"""
        df = pl.read_excel(self.file_path, sheet_name=sheet_name)

        if title not in df.columns:
            raise ValueError(f"字段 '{title}' 不存在")

        grouped = df.group_by(title).agg(pl.len()).sort("len", descending=True)

        if count_only:
            result = grouped.to_dicts()
            return {row[title]: row["len"] for row in result}
        else:
            return [
                {"value": row[title], "count": row["len"]}
                for row in grouped.to_dicts()
            ]

    def search_keyword(
        self,
        sheet_name: str,
        keyword: str,
        case_sensitive: bool
    ) -> list[dict]:
        """在 sheet 中搜索关键字"""
        df = pl.read_excel(self.file_path, sheet_name=sheet_name)

        if case_sensitive:
            pattern = keyword
        else:
            pattern = f"(?i){keyword}"

        result = df.filter(
            pl.any_horizontal(pl.col(pl.Utf8).str.contains(pattern))
        )

        return [{"_row_id": i + 1, **row} for i, row in enumerate(result.to_dicts())]

    def advanced_group_by(
        self,
        sheet_name: str,
        group_by_fields: list[str],
        aggregations: dict,
        offset: int = 0,
        limit: int = None,
        date_fields: list[str] = None
    ) -> dict:
        """高级分组统计 - 支持多字段分组和多种聚合函数"""
        if date_fields is None:
            date_fields = []

        df = pl.read_excel(self.file_path, sheet_name=sheet_name)

        # 处理日期字段
        if date_fields:
            df = self.parse_date_fields(df, date_fields)

        # 验证分组字段
        for field in group_by_fields:
            if field not in df.columns:
                raise ValueError(f"分组字段 '{field}' 不存在")

        # 构建聚合表达式
        agg_exprs = []
        for field, funcs in aggregations.items():
            if field not in df.columns:
                raise ValueError(f"聚合字段 '{field}' 不存在")

            for func in funcs:
                if func == "count":
                    agg_exprs.append(pl.col(field).count().alias(f"{field}_count"))
                elif func == "sum":
                    agg_exprs.append(pl.col(field).sum().alias(f"{field}_sum"))
                elif func == "mean":
                    agg_exprs.append(pl.col(field).mean().alias(f"{field}_mean"))
                elif func == "min":
                    agg_exprs.append(pl.col(field).min().alias(f"{field}_min"))
                elif func == "max":
                    agg_exprs.append(pl.col(field).max().alias(f"{field}_max"))
                elif func == "median":
                    agg_exprs.append(pl.col(field).median().alias(f"{field}_median"))
                elif func == "std":
                    agg_exprs.append(pl.col(field).std().alias(f"{field}_std"))
                else:
                    raise ValueError(f"不支持的聚合函数: {func}")

        # 执行分组聚合
        if not agg_exprs:
            # 如果没有聚合字段，只做分组计数
            grouped = df.group_by(group_by_fields).agg(pl.len().alias("count"))
        else:
            grouped = df.group_by(group_by_fields).agg(agg_exprs)

        # 应用 offset 和 limit
        total_count = len(grouped)
        if offset > 0:
            grouped = grouped.slice(offset, len(grouped))
        if limit is not None:
            grouped = grouped.slice(0, limit)

        result_data = grouped.to_dicts()

        return {
            "sheet_name": sheet_name,
            "group_by_fields": group_by_fields,
            "aggregations": aggregations,
            "result_count": len(result_data),
            "total_count": total_count,
            "result": result_data,
            "offset": offset,
            "limit": limit
        }

    def query_by_sql(
        self,
        sheet_name: str,
        sql_query: str,
        table_name: str = "excel_table"
    ) -> dict:
        """
        使用 SQL 语句查询数据

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
        """
        df = pl.read_excel(self.file_path, sheet_name=sheet_name)

        # 创建 SQLContext 并注册 DataFrame
        ctx = pl.SQLContext()
        ctx.register(table_name, df)

        # 执行 SQL 查询
        result_df = ctx.execute(sql_query).collect()

        return {
            "sheet_name": sheet_name,
            "sql_query": sql_query,
            "row_count": len(result_df),
            "result": result_df.to_dicts()
        }
