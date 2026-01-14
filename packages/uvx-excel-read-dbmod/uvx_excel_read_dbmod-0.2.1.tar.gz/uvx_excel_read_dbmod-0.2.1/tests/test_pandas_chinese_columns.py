"""
测试 pandas 引擎的中文列名支持
验证 pandas 和 polars 引擎的列名处理是否一致
"""
import pytest
from pathlib import Path
from uvx_excel_read_dbmod.base_mod.pandas import PandasEngine
from uvx_excel_read_dbmod.base_mod.polars import PolarsEngine


class TestChineseColumns:
    """测试中文列名处理"""

    @pytest.fixture
    def excel_file(self):
        """获取测试 Excel 文件路径"""
        return Path(__file__).parent / "2025NCR总台账.xlsx"

    @pytest.fixture
    def sheet_name(self):
        """测试用的 sheet 名称"""
        return "Sheet2"

    def test_pandas_get_row_by_id_has_chinese_columns(self, excel_file, sheet_name):
        """测试 pandas 引擎获取行数据时是否使用中文列名"""
        engine = PandasEngine(str(excel_file))
        result = engine.get_row_by_id(sheet_name, 1)

        # 验证返回的数据使用中文列名
        expected_columns = ["序号", "日期", "提醒", "来源", "NCR单号", "发现人", "项目", "物料号", "物料名称", "型号", "数量", "序列号", "故障描述", "原因分析", "纠正措施", "完成情况", "改善措施", "供应商", "备注"]

        for col in expected_columns:
            assert col in result, f"缺少中文列名: {col}"

        # 验证不应该有 Unnamed 列名
        for col in result.keys():
            assert not str(col).startswith("Unnamed:"), f"存在 Unnamed 列名: {col}"

    def test_polars_get_row_by_id_has_chinese_columns(self, excel_file, sheet_name):
        """测试 polars 引擎获取行数据时使用中文列名（对比基准）"""
        engine = PolarsEngine(str(excel_file))
        result = engine.get_row_by_id(sheet_name, 1)

        # 验证返回的数据使用中文列名
        expected_columns = ["序号", "日期", "提醒", "来源", "NCR单号", "发现人", "项目", "物料号", "物料名称", "型号", "数量", "序列号", "故障描述", "原因分析", "纠正措施", "完成情况", "改善措施", "供应商", "备注"]

        for col in expected_columns:
            assert col in result, f"缺少中文列名: {col}"

    def test_pandas_query_by_conditions_with_chinese_columns(self, excel_file, sheet_name):
        """测试 pandas 引擎使用中文列名进行条件查询"""
        engine = PandasEngine(str(excel_file))
        conditions = [{"field": "来源", "value": "售后质量"}]
        result = engine.query_by_conditions(sheet_name, conditions, "exact")

        # 验证查询成功
        assert len(result) > 0, "应该查询到数据"

        # 验证结果使用中文列名
        first_row = result[0]
        expected_columns = ["序号", "日期", "提醒", "来源", "NCR单号"]
        for col in expected_columns:
            assert col in first_row, f"缺少中文列名: {col}"

        # 不应该有 Unnamed 列名
        for col in first_row.keys():
            assert not str(col).startswith("Unnamed:"), f"存在 Unnamed 列名: {col}"

    def test_pandas_advanced_group_by_with_chinese_columns(self, excel_file, sheet_name):
        """测试 pandas 引擎使用中文列名进行高级分组统计"""
        engine = PandasEngine(str(excel_file))
        group_by_fields = ["来源", "完成情况"]
        aggregations = {"数量": ["sum"]}
        result = engine.advanced_group_by(sheet_name, group_by_fields, aggregations, limit=5)

        # 验证分组成功
        assert result["result_count"] > 0, "应该有分组结果"
        assert "分组字段 '来源' 不存在" not in str(result), "不应该报错字段不存在"

        # 验证结果包含中文列名
        if result["result_count"] > 0:
            first_result = result["result"][0]
            assert "来源" in first_result, "分组结果应该包含'来源'字段"
            assert "完成情况" in first_result, "分组结果应该包含'完成情况'字段"

    def test_pandas_and_polars_columns_consistency(self, excel_file, sheet_name):
        """测试 pandas 和 polars 引擎的列名是否一致"""
        pandas_engine = PandasEngine(str(excel_file))
        polars_engine = PolarsEngine(str(excel_file))

        pandas_row = pandas_engine.get_row_by_id(sheet_name, 1)
        polars_row = polars_engine.get_row_by_id(sheet_name, 1)

        # 验证两者的列名应该一致
        pandas_columns = set(pandas_row.keys())
        polars_columns = set(polars_row.keys())

        assert pandas_columns == polars_columns, f"pandas 和 polars 列名不一致\npandas: {pandas_columns}\npolars: {polars_columns}"

    def test_pandas_group_by_title_with_chinese_columns(self, excel_file, sheet_name):
        """测试 pandas 引擎使用中文列名进行分组统计"""
        engine = PandasEngine(str(excel_file))
        result = engine.group_by_title(sheet_name, "来源", count_only=False)

        # 验证分组成功
        assert len(result) > 0, "应该有分组结果"

        # 验证返回格式
        first_group = result[0]
        assert "value" in first_group, "分组结果应该包含'value'字段"
        assert "count" in first_group, "分组结果应该包含'count'字段"

    def test_pandas_search_keyword_with_chinese_columns(self, excel_file, sheet_name):
        """测试 pandas 引擎搜索关键字时使用中文列名"""
        engine = PandasEngine(str(excel_file))
        result = engine.search_keyword(sheet_name, "NCR", case_sensitive=False)

        # 验证搜索成功
        assert len(result) > 0, "应该搜索到数据"

        # 验证结果使用中文列名
        first_row = result[0]
        expected_columns = ["序号", "日期", "提醒", "来源"]
        for col in expected_columns:
            assert col in first_row, f"缺少中文列名: {col}"

        # 不应该有 Unnamed 列名
        for col in first_row.keys():
            assert not str(col).startswith("Unnamed:"), f"存在 Unnamed 列名: {col}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
