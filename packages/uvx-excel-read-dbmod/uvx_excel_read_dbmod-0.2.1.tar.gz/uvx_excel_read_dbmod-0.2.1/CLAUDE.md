# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于 FastMCP 的 Excel 文件读取工具，使用数据库抽象方式操作 Excel 文件。

### 核心概念

- **Sheet** = 数据库名
- **表头** = 字段名
- **行号** = ID

### 技术栈

- Python 3.12.12
- fastmcp 2.14.2
- pandas、polars
- uv (包管理和构建工具)

## 构建和发布

### 构建并发布到 Nexus3

```bash
./build_and_publish_uv.sh
```

该脚本需要：
- `.env` 文件中配置 `NEXUS_USERNAME` 和 `NEXUS_PASSWORD`
- `VERSION` 文件包含当前版本号
- Nexus3 URL 默认为 `https://nexus3.m.6do.me:4000/`

## 代码结构

```
src/
├── base_mod/     # 基础模块
└── tools/        # 工具模块，每个工具单独一个文件夹
```

## 计划实现的工具

- `get_sheet_list` - 获取所有 sheet 列表、名称
- `get_sheet_title` - 获取 sheet 的表头
- `select_count_sheet_rows` - 获取 sheet 的行数
- `select_sheet_rows_by_id` - 获取 sheet 的某一行数据
- `select_sheet_rows_by_title_where` - 根据多个表头的条件获取 sheet 的某行数据
- `group_by_count_and_values_sheet_title` - 对某个表头进行分组，统计内容、行数
- `search_row_in_sheet_by_keyword` - 在某个 sheet 中搜索某个关键字

## 开发说明

- 使用 `uv` 作为包管理工具
- 每个工具应放置在 `src/tools/` 下的独立文件夹中
- 代码需遵循 FastMCP 协议规范
