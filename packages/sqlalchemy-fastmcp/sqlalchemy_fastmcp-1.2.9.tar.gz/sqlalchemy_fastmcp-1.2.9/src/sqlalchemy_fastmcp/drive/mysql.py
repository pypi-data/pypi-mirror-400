"""
MySQL 数据库驱动
"""

from typing import Dict, Any
from .base import BaseDriver


class MySQLDriver(BaseDriver):
    """MySQL 数据库驱动"""

    @property
    def db_type(self) -> str:
        return "mysql"

    @property
    def default_port(self) -> int:
        return 3306

    def create_connection_string(self) -> str:
        """创建 MySQL 连接字符串"""
        if self.config.get("database"):
            return (
                f"mysql+pymysql://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
                f"?charset={self.config.get('charset', 'utf8mb4')}"
            )
        else:
            return (
                f"mysql+pymysql://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}"
                f"?charset={self.config.get('charset', 'utf8mb4')}"
            )

    def get_show_databases_sql(self) -> str:
        """获取显示数据库列表的 SQL"""
        return "SHOW DATABASES"

    def get_show_tables_sql(self) -> str:
        """获取显示表列表的 SQL"""
        return "SHOW TABLES"

    def get_table_comment_sql(self, table_name: str) -> str:
        """获取获取表注释的 SQL"""
        return f"""
            SELECT TABLE_COMMENT
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = '{table_name}'
        """

    def parse_table_comment(self, result: Any, table_name: str) -> str:
        """解析表注释"""
        comment = result.fetchone()
        return comment[0] if comment and comment[0] else ""

    def get_system_databases(self) -> set:
        """获取系统数据库集合"""
        return {"information_schema", "mysql", "performance_schema", "sys"}
