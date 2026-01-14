"""
Excel 单元测试 - 测试日期字段、where 条件、排序和分组功能
"""
import unittest
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uvx_excel_read_dbmod.base_mod.excel_manager import ExcelManager


class TestExcelManager(unittest.TestCase):
    """测试 ExcelManager 功能"""

    @classmethod
    def setUpClass(cls):
        """设置测试数据"""
        cls.test_file = Path(__file__).parent / "2025NCR总台账.xlsx"
        cls.sheet_name = "Sheet2"

    def test_01_basic_read(self):
        """测试基本读取功能"""
        manager = ExcelManager(str(self.test_file), engine="pandas", header_row=1)

        # 获取 sheet 列表
        sheets = manager.get_sheet_names()
        self.assertIn(self.sheet_name, sheets)

        # 获取行数
        row_count = manager.get_row_count(self.sheet_name)
        self.assertGreater(row_count, 0)
        print(f"✓ 总行数: {row_count}")

    def test_02_date_field_conversion(self):
        """测试日期字段转换"""
        import pandas as pd
        from uvx_excel_read_dbmod.base_mod.pandas import PandasEngine

        # 使用 PandasEngine 直接测试
        engine = PandasEngine(str(self.test_file), header_row=1)

        # 读取数据
        df = pd.read_excel(str(self.test_file), sheet_name=self.sheet_name, header=1)

        # 测试日期字段转换前
        print(f"  转换前日期列类型: {df['日期'].dtype}")

        # 测试日期字段转换
        df_converted = engine.parse_date_fields(df, ["日期"])

        # 验证转换后
        print(f"  转换后日期列类型: {df_converted['日期'].dtype}")
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df_converted["日期"]) or
                       pd.api.types.is_object_dtype(df_converted["日期"]))

    def test_03_where_with_date_fields(self):
        """测试 where 条件 + 日期字段"""
        manager = ExcelManager(str(self.test_file), engine="pandas", header_row=1)

        # 测试：日期 >= 2025-01-01
        result = manager.query_by_conditions(
            self.sheet_name,
            [{"field": "日期", "value": "2025-01-01"}],
            match_type="gte",
            date_fields=["日期"]
        )

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        print(f"✓ 日期 >= 2025-01-01 的记录数: {len(result)}")

    def test_04_where_with_string_contains(self):
        """测试字符串包含查询"""
        manager = ExcelManager(str(self.test_file), engine="pandas", header_row=1)

        # 测试：来源包含 "质量"
        result = manager.query_by_conditions(
            self.sheet_name,
            [{"field": "来源", "value": "质量"}],
            match_type="contains"
        )

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        print(f"✓ 来源包含 '质量' 的记录数: {len(result)}")

    def test_05_where_with_numeric_compare(self):
        """测试数值比较查询"""
        manager = ExcelManager(str(self.test_file), engine="pandas", header_row=1)

        # 测试：提醒 > 30
        result = manager.query_by_conditions(
            self.sheet_name,
            [{"field": "提醒", "value": 30}],
            match_type="gt"
        )

        self.assertIsInstance(result, list)
        # 验证结果确实都 > 30
        for row in result:
            if row["提醒"] is not None:
                self.assertGreater(row["提醒"], 30)

        print(f"✓ 提醒 > 30 的记录数: {len(result)}")

    def test_06_advanced_group_by(self):
        """测试高级分组统计"""
        manager = ExcelManager(str(self.test_file), engine="pandas", header_row=1)

        # 按 "来源" 分组，统计提醒的平均值、总和、最大值
        result = manager.advanced_group_by(
            self.sheet_name,
            group_by_fields=["来源"],
            aggregations={"提醒": ["count", "mean", "sum", "max"]},
            date_fields=["日期"]
        )

        self.assertIn("result_count", result)
        self.assertIn("result", result)
        self.assertGreater(result["result_count"], 0)

        print(f"✓ 按 '来源' 分组统计:")
        for row in result["result"][:5]:  # 只打印前 5 条
            print(f"  - {row['来源']}: count={row.get('提醒_count', 'N/A')}, max={row.get('提醒_max', 'N/A')}")

    def test_07_advanced_group_by_multi_field(self):
        """测试多字段分组统计"""
        manager = ExcelManager(str(self.test_file), engine="pandas", header_row=1)

        # 按 "来源" + "完成情况" 分组
        result = manager.advanced_group_by(
            self.sheet_name,
            group_by_fields=["来源", "完成情况"],
            aggregations={"提醒": ["count", "mean"]},
            date_fields=["日期"]
        )

        self.assertIn("result_count", result)
        self.assertGreater(result["result_count"], 0)

        print(f"✓ 按 '来源' + '完成情况' 分组统计:")
        for row in result["result"][:5]:
            print(f"  - {row['来源']} / {row.get('完成情况', 'N/A')}: count={row.get('提醒_count', 'N/A')}")

    def test_08_pagination(self):
        """测试分页功能"""
        manager = ExcelManager(str(self.test_file), engine="pandas", header_row=1)

        # 获取第一页（limit=5）
        page1 = manager.advanced_group_by(
            self.sheet_name,
            group_by_fields=["来源"],
            aggregations={"提醒": ["count"]},
            offset=0,
            limit=5
        )

        # 获取第二页（offset=5, limit=5）
        page2 = manager.advanced_group_by(
            self.sheet_name,
            group_by_fields=["来源"],
            aggregations={"提醒": ["count"]},
            offset=5,
            limit=5
        )

        self.assertEqual(len(page1["result"]), 5)
        self.assertLessEqual(len(page2["result"]), 5)

        print(f"✓ 分页测试: 第1页 {page1['result_count']} 条, 第2页 {page2['result_count']} 条")

    def test_09_search_keyword(self):
        """测试关键词搜索"""
        manager = ExcelManager(str(self.test_file), engine="pandas", header_row=1)

        # 搜索 "周登龙"
        result = manager.search_keyword(
            self.sheet_name,
            "周登龙",
            case_sensitive=False
        )

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        print(f"✓ 搜索 '周登龙': 找到 {len(result)} 条记录")

    def test_10_get_row_by_id(self):
        """测试按行号获取数据"""
        manager = ExcelManager(str(self.test_file), engine="pandas", header_row=1)

        # 获取第1行数据
        row = manager.get_row_by_id(self.sheet_name, 1)

        self.assertIn("序号", row)
        self.assertEqual(row["序号"], 1)
        print(f"✓ 第1行数据: 序号={row['序号']}, 日期={row.get('日期', 'N/A')}")


class TestPolarsEngine(unittest.TestCase):
    """测试 Polars 引擎"""

    @classmethod
    def setUpClass(cls):
        """设置测试数据"""
        cls.test_file = Path(__file__).parent / "2025NCR总台账.xlsx"
        cls.sheet_name = "Sheet2"

    def test_polars_basic_query(self):
        """测试 Polars 基本查询"""
        manager = ExcelManager(str(self.test_file), engine="polars", header_row=1)

        # 测试查询
        result = manager.query_by_conditions(
            self.sheet_name,
            [{"field": "来源", "value": "售后质量"}],
            match_type="exact"
        )

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        print(f"✓ Polars: 来源='售后质量' 的记录数: {len(result)}")

    def test_polars_group_by(self):
        """测试 Polars 分组统计"""
        manager = ExcelManager(str(self.test_file), engine="polars", header_row=1)

        result = manager.advanced_group_by(
            self.sheet_name,
            group_by_fields=["来源"],
            aggregations={"提醒": ["count", "mean"]},
            date_fields=["日期"]
        )

        self.assertIn("result_count", result)
        self.assertGreater(result["result_count"], 0)
        print(f"✓ Polars: 按 '来源' 分组统计，共 {result['result_count']} 组")


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
