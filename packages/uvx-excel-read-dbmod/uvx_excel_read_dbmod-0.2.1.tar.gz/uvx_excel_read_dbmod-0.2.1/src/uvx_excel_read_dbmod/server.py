"""
uvx-excel-read-dbmod MCP 服务器主入口
用数据库的方式提供读取、分析 Excel 文件的 MCP 服务
"""
import sys
import argparse
from pathlib import Path

# 读取版本号
def get_version():
    version_file = Path(__file__).parent.parent.parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()
    return "0.1.0"

VERSION = get_version()

# 工具列表说明
TOOLS_INFO = """
可用工具列表：

1. get_sheet_list
   获取 Excel 文件中所有 sheet 的列表和名称

2. select_count_sheet_rows
   获取指定 sheet 的行数

3. select_sheet_rows_by_id
   根据行号（ID）获取 sheet 中的某一行数据

4. select_sheet_rows_by_title_where
   根据多个表头的条件查询数据
   支持匹配类型：exact, contains, regex, gt, lt, gte, lte, in, not_in

5. group_by_sheet_title_get_count_and_values
   按表头分组统计，显示每个值的计数

6. search_row_in_sheet_by_keyword
   在 sheet 中搜索包含关键字的所有行

7. advanced_group_by
   高级分组统计，支持多字段分组和多种聚合函数
   聚合函数：count, sum, mean, min, max, median, std
   支持分页：offset, limit

8. query_by_sql
   使用 SQL 语句查询 sheet 数据（仅支持 polars 引擎）
   支持完整 SQL 语法：SELECT, WHERE, GROUP BY, ORDER BY, HAVING, LIMIT 等

所有工具均支持 pandas 和 polars 两种数据处理引擎。
所有工具均支持自定义表头行（header_row 参数）。
"""


def print_help():
    """打印帮助信息"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          uvx-excel-read-dbmod MCP 服务                        ║
╚══════════════════════════════════════════════════════════════╝

版本: {VERSION}
描述: 用数据库的方式提供读取、分析 Excel 文件的 MCP 服务

技术方案:
  - Sheet = 数据库名
  - 表头 = 字段名
  - 行号 = ID
  - 支持 pandas 和 polars 两种数据处理引擎
{TOOLS_INFO}
用法:
  uvx-excel-read-dbmod                # 启动 MCP 服务器
  uvx-excel-read-dbmod --help         # 显示此帮助信息
  uvx-excel-read-dbmod --version      # 显示版本信息
""")


def main():
    """启动 MCP 服务器"""
    # 先解析参数，处理 --help 和 --version
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--help", "-h", action="store_true", help="显示帮助信息")
    parser.add_argument("--version", "-v", action="store_true", help="显示版本信息")
    parser.add_argument("transport", nargs="?", choices=["stdio"], help="传输方式 (默认: stdio)")

    args, _ = parser.parse_known_args()

    if args.help:
        print_help()
        sys.exit(0)
    elif args.version:
        print(f"uvx-excel-read-dbmod v{VERSION}")
        sys.exit(0)

    # 导入工具注册模块
    from uvx_excel_read_dbmod.tools.get_sheet_list.tool import register_tool as register_get_sheet_list
    from uvx_excel_read_dbmod.tools.select_count_sheet_rows.tool import register_tool as register_select_count_sheet_rows
    from uvx_excel_read_dbmod.tools.select_sheet_rows_by_id.tool import register_tool as register_select_sheet_rows_by_id
    from uvx_excel_read_dbmod.tools.select_sheet_rows_by_title_where.tool import register_tool as register_select_sheet_rows_by_title_where
    from uvx_excel_read_dbmod.tools.group_by_sheet_title_get_count_and_values.tool import register_tool as register_group_by_sheet_title_get_count_and_values
    from uvx_excel_read_dbmod.tools.search_row_in_sheet_by_keyword.tool import register_tool as register_search_row_in_sheet_by_keyword
    from uvx_excel_read_dbmod.tools.advanced_group_by.tool import register_tool as register_advanced_group_by
    from uvx_excel_read_dbmod.tools.query_by_sql.tool import register_tool as register_query_by_sql

    # 创建 MCP 服务器实例
    from fastmcp import FastMCP
    mcp = FastMCP("uvx-excel-read-dbmod")

    # 注册所有工具
    register_get_sheet_list(mcp)
    register_select_count_sheet_rows(mcp)
    register_select_sheet_rows_by_id(mcp)
    register_select_sheet_rows_by_title_where(mcp)
    register_group_by_sheet_title_get_count_and_values(mcp)
    register_search_row_in_sheet_by_keyword(mcp)
    register_advanced_group_by(mcp)
    register_query_by_sql(mcp)

    mcp.run()


if __name__ == "__main__":
    main()
