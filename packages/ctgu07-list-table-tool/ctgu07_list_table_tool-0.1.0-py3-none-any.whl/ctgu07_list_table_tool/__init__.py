"""
FastMCP quickstart example.

Run from the repository root:
    uv run examples/snippets/servers/fastmcp_quickstart.py
"""
import json
import os
from typing import List, Optional

from langchain_core.tools import BaseTool
from loguru import logger
from mcp.server.fastmcp import FastMCP
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

#获取当前项目的绝对路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
log_dir = os.path.join(root_dir,"logs")                #存放项目日志目录的绝对路径

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

LOG_FILE = "translation.log"

# 打印错误日志的工具类
class MyLogger:
    def __init__(self):
        self.logger = logger
        self.logger.remove()
        log_file_path = os.path.join(log_dir,LOG_FILE)
        self.logger.add(log_file_path,
                        level="DEBUG",
                        encoding = 'UTF-8',
                        format="{time:YYYYMMDD HH:mm:ss}-{process.name} | {thread.name} | {module}.{function}:{line}-{level}-{message}",
                        rotation='10 MB',
                        retention=20
                        )

    def get_logger(self):
        return self.logger

log = MyLogger().get_logger()

class MySQLDatabaseManager:
    """MySQL数据库管理器，负责数据库连接和基本操作"""

    def __init__(self, connection_string: str):
        """
        初始化MySQL数据库连接

        Args:
            connection_string: MySQL连接字符串，格式为:
                mysql+pymysql://username:password@host:port/database
        """
        self.engine = create_engine(connection_string, pool_size=5, pool_recycle=3600)

    def get_table_names(self) -> list[str]:
        """
        获取数据库中所有表的名称

        Returns:
            列表，包含数据库中所有表的名称
        """
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception as e:
            log.exception(e)
            raise ValueError(f"获取表名失败：{str(e)}")

    def get_tables_with_comments(self) -> List[dict]:
        """
        获取数据库中所有表的名称和描述信息。

        Returns:
            List[dict]: 一个字典列表，每个字典包含 'table_name' 和 'table_comment' 键。
        """
        try:
            # 构建查询语句，从 INFORMATION_SCHEMA.TABLES 中获取表名和注释
            query = text("""
                         SELECT TABLE_NAME, TABLE_COMMENT
                         FROM INFORMATION_SCHEMA.TABLES
                         WHERE TABLE_SCHEMA = DATABASE()
                           AND TABLE_TYPE = 'BASE TABLE'
                         ORDER BY TABLE_NAME
                         """)

            with self.engine.connect() as connection:
                result = connection.execute(query)
                # 将结果转换为字典列表，便于后续处理
                tables_info = [{'table_name': row[0], 'table_comment': row[1]} for row in result]
                return tables_info

        except SQLAlchemyError as e:
            log.error(e)
            raise ValueError(f"获取表名及描述信息失败：{str(e)}")

    def get_table_schema(self, table_names: Optional[List[str]] = None) -> str:
        """
        获取指定表的模式信息（包含字段注释）

        Args:
            table_names: 表名列表，如果为None则获取所有表
        """
        try:
            inspector = inspect(self.engine)
            schema_info = []

            tables_to_process = table_names if table_names else self.get_table_names()

            for table_name in tables_to_process:
                # 获取表结构信息
                columns = inspector.get_columns(table_name)

                # 使用 get_pk_constraint 替代已弃用的 get_primary_keys
                pk_constraint = inspector.get_pk_constraint(table_name)
                primary_keys = pk_constraint['constrained_columns'] if pk_constraint else []

                foreign_keys = inspector.get_foreign_keys(table_name)
                indexes = inspector.get_indexes(table_name)

                # 构建表模式描述
                table_schema = f"表名: {table_name}\n"
                table_schema += "列信息:\n"

                for column in columns:
                    # 检查该列是否在主键列表中
                    pk_indicator = " (主键)" if column['name'] in primary_keys else ""
                    # 获取字段注释，如果不存在则显示“无注释”
                    comment = column.get('comment', '无注释')
                    table_schema += f"  - {column['name']}: {str(column['type'])}{pk_indicator} [注释: {comment}]\n"

                if foreign_keys:
                    table_schema += "外键约束:\n"
                    for fk in foreign_keys:
                        table_schema += f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n"

                if indexes:
                    table_schema += "索引信息:\n"
                    for idx in indexes:
                        if not idx['name'].startswith('sqlite_'):
                            table_schema += f"  - {idx['name']}: {idx['column_names']} ({'唯一' if idx['unique'] else '非唯一'})\n"

                schema_info.append(table_schema)

            return "\n".join(schema_info) if schema_info else "未找到匹配的表"

        except SQLAlchemyError as e:
            log.error(e)
            raise ValueError(f"获取表模式失败: {str(e)}")

    def execute_query(self, query: str) -> str:
        """
        执行SQL查询并返回结果

        Args:
            query: SQL查询语句
        """
        # 安全检查：防止数据修改操作
        forbidden_keywords = ['insert', 'update', 'delete', 'drop', 'alter', 'create', 'grant', 'truncate']
        query_lower = query.lower().strip()

        # 检查是否以SELECT开头（允许子查询等复杂情况）
        if not query_lower.startswith(('select', 'with')) and any(
                keyword in query_lower for keyword in forbidden_keywords):
            raise ValueError("出于安全考虑，只允许执行SELECT查询和WITH查询")

        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))

                # 获取列名
                columns = result.keys()

                # 获取数据（限制返回行数防止内存溢出）
                rows = result.fetchmany(100)

                if not rows:
                    return "查询结果为空"

                # 格式化结果
                result_data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        # 处理无法序列化的数据类型
                        try:
                            # 尝试JSON序列化来检测是否可序列化
                            if row[i] is not None:
                                json.dumps(row[i])
                            row_dict[col] = row[i]
                        except (TypeError, ValueError):
                            row_dict[col] = str(row[i])
                    result_data.append(row_dict)

                return json.dumps(result_data, ensure_ascii=False, indent=2)
        except SQLAlchemyError as e:
            log.error(e)
            raise ValueError(f"sql执行错误：{str(e)}")

    def validate_query(self, query: str) -> str:
        """
        验证SQL查询语法是否正确

        Args:
            query: 要验证的SQL查询
        """
        # 基本语法检查
        if not query or not query.strip():
            return "错误：查询不能为空"

        # 检查是否以SELECT或WITH开头
        query_lower = query.lower().strip()
        if not query_lower.startswith(('select', 'with')):
            return "警告：建议使用SELECT或WITH查询，其他操作可能被限制"

        try:
            with self.engine.connect() as connection:
                if self.engine.dialect.name == 'mysql':
                    explain_query = text(f"EXPLAIN {query}")  # 可以利用解释器来判断SQL语句是不是正确的
                else:
                    explain_query = text(f"EXPLAIN {query}")
                connection.execute(explain_query)
                return "SQL查询语法正确(已通过数据库EXPLAIN验证)"
        except Exception as e:
            log.error(e)
            return f"SQL语法错误: {str(e)}"

class PostgreDatabaseManager:
    """MySQL数据库管理器，负责数据库连接和基本操作"""

    def __init__(self, connection_string: str):
        """
        初始化PostgreSQL数据库连接
        """
        self.engine = create_engine(connection_string, pool_size=5, pool_recycle=3600,client_encoding = 'utf8')

    def get_table_names(self) -> list[str]:
        """
        获取数据库中所有表的名称

        Returns:
            列表，包含数据库中所有表的名称
        """
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names(schema='public')
        except Exception as e:
            log.exception(e)
            raise ValueError(f"获取表名失败：{str(e)}")

    def get_tables_with_comments(self) -> List[dict]:
        """
        获取数据库中所有表的名称和描述信息。

        Returns:
            List[dict]: 一个字典列表，每个字典包含 'table_name' 和 'table_comment' 键。
        """
        try:
            # 构建查询语句，从 INFORMATION_SCHEMA.TABLES 中获取表名和注释
            query = text("""
                            SELECT 
                                c.relname AS table_name,
                                COALESCE(pg_catalog.obj_description(c.oid, 'pg_class'), '无注释') AS table_comment
                            FROM 
                                pg_catalog.pg_class c
                            LEFT JOIN 
                                pg_catalog.pg_namespace n ON n.oid = c.relnamespace
                            WHERE 
                                c.relkind = 'r'
                                AND n.nspname = 'public'
                                AND c.relname NOT LIKE 'pg_%'
                                AND c.relname NOT LIKE 'sql_%'
                            ORDER BY 
                                c.relname;
                         """)

            with self.engine.connect() as connection:
                result = connection.execute(query)
                # 将结果转换为字典列表，便于后续处理
                tables_info = [{'table_name': row[0], 'table_comment': row[1]} for row in result]
                return tables_info

        except SQLAlchemyError as e:
            log.error(e)
            raise ValueError(f"获取表名及描述信息失败：{str(e)}")

    def get_table_schema(self, table_names: Optional[List[str]] = None) -> str:
        """
        获取指定表的模式信息（包含字段注释）

        Args:
            table_names: 表名列表，如果为None则获取所有表
        """
        try:
            inspector = inspect(self.engine)
            schema_info = []

            tables_to_process = table_names if table_names else self.get_table_names()

            for table_name in tables_to_process:
                # 获取表结构信息
                columns = inspector.get_columns(table_name)

                # 使用 get_pk_constraint 替代已弃用的 get_primary_keys
                pk_constraint = inspector.get_pk_constraint(table_name)
                primary_keys = pk_constraint['constrained_columns'] if pk_constraint else []

                foreign_keys = inspector.get_foreign_keys(table_name)
                indexes = inspector.get_indexes(table_name)

                # 构建表模式描述
                table_schema = f"表名: {table_name}\n"
                table_schema += "列信息:\n"

                for column in columns:
                    # 检查该列是否在主键列表中
                    pk_indicator = " (主键)" if column['name'] in primary_keys else ""
                    # 获取字段注释，如果不存在则显示“无注释”
                    comment = column.get('comment', '无注释')
                    table_schema += f"  - {column['name']}: {str(column['type'])}{pk_indicator} [注释: {comment}]\n"

                if foreign_keys:
                    table_schema += "外键约束:\n"
                    for fk in foreign_keys:
                        table_schema += f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}\n"

                if indexes:
                    table_schema += "索引信息:\n"
                    for idx in indexes:
                        if not idx['name'].startswith('sqlite_'):
                            table_schema += f"  - {idx['name']}: {idx['column_names']} ({'唯一' if idx['unique'] else '非唯一'})\n"

                schema_info.append(table_schema)

            return "\n".join(schema_info) if schema_info else "未找到匹配的表"

        except SQLAlchemyError as e:
            log.error(e)
            raise ValueError(f"获取表模式失败: {str(e)}")

    def execute_query(self, query: str) -> str:
        """
        执行SQL查询并返回结果

        Args:
            query: SQL查询语句
        """
        # 安全检查：防止数据修改操作
        forbidden_keywords = ['insert', 'update', 'delete', 'drop', 'alter', 'create', 'grant', 'truncate']
        query_lower = query.lower().strip()

        # 检查是否以SELECT开头（允许子查询等复杂情况）
        if not query_lower.startswith(('select', 'with')) and any(
                keyword in query_lower for keyword in forbidden_keywords):
            raise ValueError("出于安全考虑，只允许执行SELECT查询和WITH查询")

        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))

                # 获取列名
                columns = result.keys()

                # 获取数据（限制返回行数防止内存溢出）
                rows = result.fetchmany(100)

                if not rows:
                    return "查询结果为空"

                # 格式化结果
                result_data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        # 处理无法序列化的数据类型
                        try:
                            # 尝试JSON序列化来检测是否可序列化
                            if row[i] is not None:
                                json.dumps(row[i])
                            row_dict[col] = row[i]
                        except (TypeError, ValueError):
                            row_dict[col] = str(row[i])
                    result_data.append(row_dict)

                return json.dumps(result_data, ensure_ascii=False, indent=2)
        except SQLAlchemyError as e:
            log.error(e)
            raise ValueError(f"sql执行错误：{str(e)}")

    def validate_query(self, query: str) -> str:
        """
        验证SQL查询语法是否正确

        Args:
            query: 要验证的SQL查询
        """
        # 基本语法检查
        if not query or not query.strip():
            return "错误：查询不能为空"

        # 检查是否以SELECT或WITH开头
        query_lower = query.lower().strip()
        if not query_lower.startswith(('select', 'with')):
            return "警告：建议使用SELECT或WITH查询，其他操作可能被限制"

        try:
            with self.engine.connect() as connection:
                if self.engine.dialect.name == 'mysql':
                    explain_query = text(f"EXPLAIN {query}")  # 可以利用解释器来判断SQL语句是不是正确的
                else:
                    explain_query = text(f"EXPLAIN {query}")
                connection.execute(explain_query)
                return "SQL查询语法正确(已通过数据库EXPLAIN验证)"
        except Exception as e:
            log.error(e)
            return f"SQL语法错误: {str(e)}"

class PostgresqlListTablesTool(BaseTool):
    """列出数据库中的所有表及其描述信息"""
    name: str = "sql_db_list_tables"
    description: str = "列出MySQL数据库中的所有表名及其描述信息。"

    # 数据库管理器实例
    db_manager: PostgreDatabaseManager

    def _run(self) -> str:
        """列出数据库中的所有表及其描述信息"""
        try:
            tables_info = self.db_manager.get_tables_with_comments()
            result = f"数据库中共有 {len(tables_info)} 个表:\n\n"
            for i, table_info in enumerate(tables_info):
                table_name = table_info['table_name']
                table_comment = table_info['table_comment']

                # 处理空描述的情况
                if not table_comment or table_comment.isspace():
                    description_display = "(暂无描述)"
                else:
                    description_display = table_comment

                result += f"{i + 1}. 表名: {table_name}\n"
                result += f"   描述: {description_display}\n\n"
            return result
        except Exception as e:
            log.exception(e)
            return f"列出表信息时出错: {str(e)}"

    async def _arun(self) -> str:
        """异步执行"""
        return self._run()

class MysqlListTablesTool(BaseTool):
    """列出数据库中的所有表及其描述信息"""
    name: str = "sql_db_list_tables"
    description: str = "列出MySQL数据库中的所有表名及其描述信息。"

    # 数据库管理器实例
    db_manager: MySQLDatabaseManager

    def _run(self) -> str:
        """列出数据库中的所有表及其描述信息"""
        try:
            tables_info = self.db_manager.get_tables_with_comments()
            result = f"数据库中共有 {len(tables_info)} 个表:\n\n"
            for i, table_info in enumerate(tables_info):
                table_name = table_info['table_name']
                table_comment = table_info['table_comment']

                # 处理空描述的情况
                if not table_comment or table_comment.isspace():
                    description_display = "(暂无描述)"
                else:
                    description_display = table_comment

                result += f"{i + 1}. 表名: {table_name}\n"
                result += f"   描述: {description_display}\n\n"
            return result
        except Exception as e:
            log.exception(e)
            return f"列出表信息时出错: {str(e)}"

    async def _arun(self) -> str:
        """异步执行"""
        return self._run()

# Create an MCP server
mcp = FastMCP("ListTablesTool", json_response=True)

# Add an addition tool
@mcp.tool()
def list_tables_tool(connection_config: str) -> str:
    """根据数据库类型和数据库连接配置,列出数据库中的所有表及其描述信息"""
    # connection_string = f"postgresql+psycopg2://wcpadmin:ctgu2025@172.16.12.43:30235/postgres?client_encoding=utf8"
    # connection_string = f"mysql+pymysql://root:123456@localhost:3306/foodmart2"
    if connection_config.lower().startswith("postgresql"):
        db_manager = PostgreDatabaseManager(connection_config)
        tool = PostgresqlListTablesTool(db_manager=db_manager)
    else:
        db_manager = MySQLDatabaseManager(connection_config)
        tool = MysqlListTablesTool(db_manager=db_manager)

    return tool.invoke({})


def main() -> None:
    mcp.run(transport='stdio')


