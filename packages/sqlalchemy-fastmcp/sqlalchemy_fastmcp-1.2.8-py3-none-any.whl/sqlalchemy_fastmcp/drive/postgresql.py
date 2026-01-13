"""
PostgreSQL 数据库驱动
"""

from typing import Dict, Any
from .base import BaseDriver


class PostgreSQLDriver(BaseDriver):
    """PostgreSQL 数据库驱动"""

    @property
    def db_type(self) -> str:
        return "postgresql"

    @property
    def default_port(self) -> int:
        return 5432

    def create_connection_string(self) -> str:
        """创建 PostgreSQL 连接字符串"""
        if self.config.get("database"):
            return (
                f"postgresql+psycopg2://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
        else:
            return (
                f"postgresql+psycopg2://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}"
            )

    def get_show_databases_sql(self) -> str:
        """获取显示数据库列表的 SQL"""
        return "SELECT datname FROM pg_database WHERE datistemplate = false"

    def get_show_tables_sql(self) -> str:
        """获取显示表列表的 SQL"""
        return "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"

    def get_table_comment_sql(self, table_name: str) -> str:
        """获取获取表注释的 SQL"""
        return f"""
            SELECT obj_description(
                ('public.{table_name}'::regclass)::oid,
                'pg_class'
            ) as table_comment
        """

    def parse_table_comment(self, result: Any, table_name: str) -> str:
        """解析表注释"""
        comment = result.fetchone()
        return comment[0] if comment and comment[0] else ""

    def get_system_databases(self) -> set:
        """获取系统数据库集合"""
        return {"postgres", "template0", "template1"}
