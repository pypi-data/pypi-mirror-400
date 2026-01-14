"""
query_by_sql 工具单元测试
"""
import unittest
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uvx_excel_read_dbmod.base_mod.excel_manager import ExcelManager


class TestQueryBySQL(unittest.TestCase):
    """测试 query_by_sql 功能"""

    @classmethod
    def setUpClass(cls):
        """设置测试数据"""
        cls.test_file = Path(__file__).parent / "2025NCR总台账.xlsx"
        cls.sheet_name = "Sheet2"

    def test_01_sql_simple_select(self):
        """测试简单的 SQL SELECT 查询"""
        manager = ExcelManager(str(self.test_file), engine="polars", header_row=1)

        # 简单查询：选择前 10 条记录
        result = manager.query_by_sql(
            self.sheet_name,
            "SELECT * FROM excel_table LIMIT 10"
        )

        self.assertIn("result", result)
        self.assertNotIn("error", result)
        self.assertEqual(result["row_count"], 10)
        self.assertGreater(len(result["result"]), 0)

        # 验证返回的数据结构
        first_row = result["result"][0]
        self.assertIn("序号", first_row)
        print(f"✓ 简单 SELECT 查询: 返回 {result['row_count']} 行")

    def test_02_sql_where_clause(self):
        """测试 SQL WHERE 子句"""
        manager = ExcelManager(str(self.test_file), engine="polars", header_row=1)

        # 查询：提醒 > 100
        result = manager.query_by_sql(
            self.sheet_name,
            "SELECT 序号, 日期, 提醒, 来源 FROM excel_table WHERE 提醒 > 100"
        )

        self.assertNotIn("error", result)
        self.assertGreater(result["row_count"], 0)

        # 验证所有结果都满足条件
        for row in result["result"]:
            if row["提醒"] is not None:
                self.assertGreater(row["提醒"], 100)

        print(f"✓ WHERE 查询 (提醒 > 100): 返回 {result['row_count']} 行")

    def test_03_sql_like_pattern(self):
        """测试 SQL LIKE 模式匹配"""
        manager = ExcelManager(str(self.test_file), engine="polars", header_row=1)

        # 查询：来源包含 '质量'
        result = manager.query_by_sql(
            self.sheet_name,
            "SELECT 来源, COUNT(*) AS 数量 FROM excel_table WHERE 来源 LIKE '%质量%' GROUP BY 来源"
        )

        self.assertNotIn("error", result)
        self.assertGreater(result["row_count"], 0)

        print(f"✓ LIKE 查询 (来源包含'质量'): 返回 {result['row_count']} 组")

    def test_04_sql_group_by(self):
        """测试 SQL GROUP BY 分组"""
        manager = ExcelManager(str(self.test_file), engine="polars", header_row=1)

        # 按 "来源" 分组统计
        result = manager.query_by_sql(
            self.sheet_name,
            """
            SELECT 来源, COUNT(*) AS 数量
            FROM excel_table
            GROUP BY 来源
            ORDER BY 数量 DESC
            """
        )

        self.assertNotIn("error", result)
        self.assertGreater(result["row_count"], 0)

        # 验证结果结构
        first_row = result["result"][0]
        self.assertIn("来源", first_row)
        self.assertIn("数量", first_row)

        print(f"✓ GROUP BY 查询: 按 '来源' 分组，共 {result['row_count']} 组")

    def test_05_sql_aggregation_functions(self):
        """测试 SQL 聚合函数"""
        manager = ExcelManager(str(self.test_file), engine="polars", header_row=1)

        # 使用多种聚合函数
        result = manager.query_by_sql(
            self.sheet_name,
            """
            SELECT
                来源,
                COUNT(*) AS 数量,
                AVG(提醒) AS 平均值,
                SUM(提醒) AS 总和,
                MAX(提醒) AS 最大值,
                MIN(提醒) AS 最小值
            FROM excel_table
            GROUP BY 来源
            ORDER BY 数量 DESC
            LIMIT 5
            """
        )

        self.assertNotIn("error", result)
        self.assertGreater(result["row_count"], 0)

        # 验证聚合字段存在
        first_row = result["result"][0]
        self.assertIn("数量", first_row)
        self.assertIn("平均值", first_row)
        self.assertIn("总和", first_row)
        self.assertIn("最大值", first_row)
        self.assertIn("最小值", first_row)

        print(f"✓ 聚合函数查询: 返回 {result['row_count']} 行")
        for row in result["result"][:3]:
            avg_val = f"{row['平均值']:.1f}" if row['平均值'] is not None else "N/A"
            print(f"  - {row['来源']}: 数量={row['数量']}, 平均值={avg_val}")

    def test_06_sql_multi_field_group_by(self):
        """测试多字段 GROUP BY"""
        manager = ExcelManager(str(self.test_file), engine="polars", header_row=1)

        # 按 "来源" 和 "完成情况" 分组
        result = manager.query_by_sql(
            self.sheet_name,
            """
            SELECT 来源, 完成情况, COUNT(*) AS 数量
            FROM excel_table
            GROUP BY 来源, 完成情况
            ORDER BY 数量 DESC
            LIMIT 10
            """
        )

        self.assertNotIn("error", result)
        self.assertGreater(result["row_count"], 0)

        print(f"✓ 多字段 GROUP BY: 按 '来源' + '完成情况' 分组，返回 {result['row_count']} 行")

    def test_07_sql_order_by(self):
        """测试 SQL ORDER BY 排序"""
        manager = ExcelManager(str(self.test_file), engine="polars", header_row=1)

        # 按 "提醒" 降序排序
        result = manager.query_by_sql(
            self.sheet_name,
            "SELECT 序号, 提醒 FROM excel_table ORDER BY 提醒 DESC LIMIT 5"
        )

        self.assertNotIn("error", result)
        self.assertEqual(result["row_count"], 5)

        # 验证是否按降序排列
        values = [row["提醒"] for row in result["result"] if row["提醒"] is not None]
        self.assertEqual(values, sorted(values, reverse=True))

        print(f"✓ ORDER BY 查询: 按 '提醒' 降序，前 5 条")

    def test_08_sql_complex_query(self):
        """测试复杂 SQL 查询"""
        manager = ExcelManager(str(self.test_file), engine="polars", header_row=1)

        # 复杂查询：多条件 + 分组 + 排序 + 限制
        result = manager.query_by_sql(
            self.sheet_name,
            """
            SELECT
                来源,
                完成情况,
                COUNT(*) AS 数量,
                AVG(提醒) AS 平均提醒,
                MAX(提醒) AS 最大提醒
            FROM excel_table
            WHERE 提醒 > 0
            GROUP BY 来源, 完成情况
            HAVING COUNT(*) > 0
            ORDER BY 最大提醒 DESC
            LIMIT 10
            """
        )

        self.assertNotIn("error", result)
        self.assertGreater(result["row_count"], 0)

        print(f"✓ 复杂查询: WHERE + GROUP BY + HAVING + ORDER BY + LIMIT")
        for row in result["result"][:3]:
            print(f"  - {row['来源']} / {row.get('完成情况', 'N/A')}: 数量={row['数量']}, 最大提醒={row['最大提醒']}")

    def test_09_sql_custom_table_name(self):
        """测试自定义表名"""
        manager = ExcelManager(str(self.test_file), engine="polars", header_row=1)

        # 使用自定义表名 "my_table"
        result = manager.query_by_sql(
            self.sheet_name,
            "SELECT COUNT(*) AS 总数 FROM my_table",
            table_name="my_table"
        )

        self.assertNotIn("error", result)
        self.assertEqual(result["row_count"], 1)
        self.assertGreater(result["result"][0]["总数"], 0)

        print(f"✓ 自定义表名: 使用 'my_table'，总记录数={result['result'][0]['总数']}")

    def test_10_pandas_engine_not_supported(self):
        """测试 pandas 引擎不支持 SQL"""
        manager = ExcelManager(str(self.test_file), engine="pandas", header_row=1)

        result = manager.query_by_sql(
            self.sheet_name,
            "SELECT * FROM excel_table LIMIT 1"
        )

        # 应该返回错误信息
        self.assertIn("error", result)
        self.assertIn("polars", result["error"])

        print(f"✓ pandas 引擎正确返回错误提示")


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
