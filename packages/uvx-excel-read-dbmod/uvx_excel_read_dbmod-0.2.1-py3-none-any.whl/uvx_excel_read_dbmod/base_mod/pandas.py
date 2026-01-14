"""
Pandas 引擎 - 使用 pandas 处理 Excel 文件
"""
import pandas as pd
from pathlib import Path
from typing import Optional, Literal, Union, List


class PandasEngine:
    """Pandas 数据处理引擎"""

    def __init__(self, file_path: str, header_row: int = 0):
        """
        初始化 Pandas 引擎

        Args:
            file_path: Excel 文件路径
            header_row: 表头所在的行号（从 0 开始），默认 0
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        self.header_row = header_row
        self._column_mapping = {}  # 存储列名映射：Unnamed: X -> 中文列名

    def _read_excel_with_clean_columns(self, sheet_name: str, **kwargs) -> pd.DataFrame:
        """
        读取 Excel 并清理列名，使其与 polars 引擎保持一致

        Args:
            sheet_name: sheet 名称
            **kwargs: 传递给 read_excel 的其他参数

        Returns:
            清理列名后的 DataFrame
        """
        df = pd.read_excel(self.file_path, sheet_name=sheet_name, **kwargs)

        # 清理列名：将 Unnamed: X 替换为实际的中文列名
        new_columns = {}
        for i, col in enumerate(df.columns):
            if str(col).startswith('Unnamed:'):
                # 检查第一行数据，获取实际的列名
                if not df.empty:
                    first_row_value = df.iloc[0, i]
                    # 如果第一行是字符串且不是 NaN，则作为列名
                    if pd.notna(first_row_value) and isinstance(first_row_value, str):
                        new_columns[col] = first_row_value

        if new_columns:
            # 重命名列
            df = df.rename(columns=new_columns)
            # 保存映射关系
            self._column_mapping.update(new_columns)
            # 删除第一行（因为它是列名）
            df = df.iloc[1:].reset_index(drop=True)

        return df

    def get_sheet_names(self) -> list[str]:
        """获取所有 sheet 名称"""
        return pd.ExcelFile(self.file_path).sheet_names

    def get_title(self, sheet_name: str) -> list[str]:
        """获取 sheet 的表头（字段名）"""
        df = self._read_excel_with_clean_columns(sheet_name, header=self.header_row, nrows=1)
        return df.columns.tolist()

    def get_row_count(self, sheet_name: str) -> int:
        """获取 sheet 的行数"""
        df = self._read_excel_with_clean_columns(sheet_name, header=self.header_row, usecols=[0])
        return len(df)

    def get_row_by_id(self, sheet_name: str, row_id: int) -> dict:
        """根据 ID（行号）获取数据"""
        df = self._read_excel_with_clean_columns(sheet_name, header=self.header_row)
        if row_id > len(df):
            raise ValueError(f"行号 {row_id} 超出范围，总行数: {len(df)}")
        row = df.iloc[row_id - 1]
        return {col: row[col] for col in df.columns}

    def parse_date_fields(self, df: pd.DataFrame, date_fields: list[str]) -> pd.DataFrame:
        """
        将指定字段转换为日期类型

        Args:
            df: pandas DataFrame
            date_fields: 需要转换为日期的字段列表

        Returns:
            转换后的 DataFrame
        """
        if not date_fields:
            return df

        for field in date_fields:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field], errors="coerce")

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

        df = self._read_excel_with_clean_columns(sheet_name, header=self.header_row)

        # 处理日期字段
        if date_fields:
            df = self.parse_date_fields(df, date_fields)

        mask = pd.Series([True] * len(df))

        for condition in conditions:
            field = condition.get("field")
            value = condition.get("value")

            if field not in df.columns:
                raise ValueError(f"字段 '{field}' 不存在")

            if match_type == "exact":
                mask &= (df[field] == value)
            elif match_type == "contains":
                mask &= df[field].astype(str).str.contains(str(value), na=False)
            elif match_type == "regex":
                mask &= df[field].astype(str).str.match(str(value), na=False)
            elif match_type == "gt":
                mask &= (df[field] > value)
            elif match_type == "lt":
                mask &= (df[field] < value)
            elif match_type == "gte":
                mask &= (df[field] >= value)
            elif match_type == "lte":
                mask &= (df[field] <= value)
            elif match_type == "in":
                mask &= df[field].isin(value)
            elif match_type == "not_in":
                mask &= ~df[field].isin(value)

        result_df = df[mask]
        return result_df.to_dict(orient="records")

    def group_by_title(
        self,
        sheet_name: str,
        title: str,
        count_only: bool
    ) -> Union[dict, list[dict]]:
        """按表头分组统计"""
        df = self._read_excel_with_clean_columns(sheet_name, header=self.header_row)

        if title not in df.columns:
            raise ValueError(f"字段 '{title}' 不存在")

        grouped = df.groupby(title).size().sort_values(ascending=False)

        if count_only:
            return grouped.to_dict()
        else:
            return [
                {"value": val, "count": count}
                for val, count in grouped.items()
            ]

    def search_keyword(
        self,
        sheet_name: str,
        keyword: str,
        case_sensitive: bool
    ) -> list[dict]:
        """在 sheet 中搜索关键字"""
        df = self._read_excel_with_clean_columns(sheet_name, header=self.header_row)

        mask = pd.Series([False] * len(df))
        for col in df.columns:
            if case_sensitive:
                mask |= df[col].astype(str).str.contains(keyword, na=False)
            else:
                mask |= df[col].astype(str).str.contains(keyword, case=False, na=False)

        result_df = df[mask].reset_index(drop=True)
        result = []
        for idx, row in result_df.iterrows():
            row_dict = row.to_dict()
            row_dict["_row_id"] = idx + 1
            result.append(row_dict)
        return result

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

        df = self._read_excel_with_clean_columns(sheet_name, header=self.header_row)

        # 处理日期字段
        if date_fields:
            df = self.parse_date_fields(df, date_fields)

        # 验证分组字段
        for field in group_by_fields:
            if field not in df.columns:
                raise ValueError(f"分组字段 '{field}' 不存在")

        # 构建 agg 字典
        agg_dict = {}
        for field, funcs in aggregations.items():
            if field not in df.columns:
                raise ValueError(f"聚合字段 '{field}' 不存在")

            agg_funcs = []
            for func in funcs:
                if func == "count":
                    agg_funcs.append("count")
                elif func == "sum":
                    agg_funcs.append("sum")
                elif func == "mean":
                    agg_funcs.append("mean")
                elif func == "min":
                    agg_funcs.append("min")
                elif func == "max":
                    agg_funcs.append("max")
                elif func == "median":
                    agg_funcs.append("median")
                elif func == "std":
                    agg_funcs.append("std")
                else:
                    raise ValueError(f"不支持的聚合函数: {func}")

            agg_dict[field] = agg_funcs

        # 执行分组聚合
        if not agg_dict:
            # 如果没有聚合字段，只做分组计数
            grouped = df.groupby(group_by_fields).size().reset_index(name="count")
            result_data = grouped.to_dict(orient="records")
        else:
            grouped = df.groupby(group_by_fields).agg(agg_dict)
            # 展平多级列名
            grouped.columns = ["_".join(col).strip() for col in grouped.columns.values]
            result_data = grouped.reset_index().to_dict(orient="records")

        # 应用 offset 和 limit
        total_count = len(result_data)
        if offset > 0:
            result_data = result_data[offset:]
        if limit is not None:
            result_data = result_data[:limit]

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
        使用 SQL 语句查询数据（pandas 不支持，请使用 polars 引擎）

        Args:
            sheet_name: sheet 名称
            sql_query: SQL 查询语句
            table_name: 注册到 SQLContext 的表名

        Returns:
            错误信息字典
        """
        return {
            "error": "SQL 查询功能仅支持 polars 引擎，请使用 engine='polars'",
            "sheet_name": sheet_name,
            "sql_query": sql_query,
            "row_count": 0,
            "result": []
        }
