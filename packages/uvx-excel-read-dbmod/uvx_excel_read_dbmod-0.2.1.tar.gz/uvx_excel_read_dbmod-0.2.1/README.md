### 项目
- python 3.12.12
- fastmcp 2.14.2
- pandas、polars
- 单元测试用 unittest 
- 测试用例在 tests 文件夹下
- 目的是为了解决，读取Excel 会返回整个表信息，导致token 爆炸的问题，而用数据库的形式，可以让LLM 逐步进行数据分析，避免token 爆炸的问题。

### 技术方案
- 是用 uv 管理和打包，.venv 为虚拟环境目录
- 用DB 的方式提供读取、分析 Excel
- Sheet = Dbname
- 表头就是字段
- 行号 = id
- 提供 pandas 和 polars 两种数据处理方式

### 文件夹
- src
  - tools 每个工具单独一个文件夹 


### tools
- get_sheet_list 获取所有sheet 列表、名称
- select_count_sheet_rows 获取 sheet 的行数
- select_sheet_rows_by_id 获取 sheet 的某一行数据
- select_sheet_rows_by_title_where 根据多个表头的条件(可以完全匹配、模糊匹配、正则匹配、大于小于、区间、包含、不包含) 获取 sheet 的某行数据
- group_by_sheet_title_get_count_and_values 对某个表头进行分组，统计内容、行数
- search_row_in_sheet_by_keyword 在某个sheet 中搜索某个关键字
- query_by_sql 使用 SQL 语句查询 sheet 数据，支持完整的 SQL 语法（SELECT、WHERE、GROUP BY、ORDER BY、HAVING、LIMIT 等），使用 polars SQLContext 实现