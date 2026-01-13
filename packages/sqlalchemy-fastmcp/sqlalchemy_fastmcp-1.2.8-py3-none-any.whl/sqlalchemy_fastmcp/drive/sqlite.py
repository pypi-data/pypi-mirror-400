"""
SQLite 数据库驱动
"""

import re
from typing import Dict, Any, Optional
from .base import BaseDriver
from sqlalchemy import text


class SQLiteDriver(BaseDriver):
    """SQLite 数据库驱动"""

    @property
    def db_type(self) -> str:
        return "sqlite"

    @property
    def default_port(self) -> int:
        return 0

    def create_connection_string(self) -> str:
        """创建 SQLite 连接字符串"""
        db_path = self.config.get("database", "database.db")
        if not db_path:
            db_path = "database.db"
        return f"sqlite:///{db_path}"

    def get_show_databases_sql(self) -> str:
        """获取显示数据库列表的 SQL（SQLite 不支持）"""
        return "SELECT 'sqlite' as database"

    def get_show_tables_sql(self) -> str:
        """获取显示表列表的 SQL"""
        return "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"

    def get_table_comment_sql(self, table_name: str) -> str:
        """获取获取表注释的 SQL"""
        return (
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )

    def parse_table_comment(self, result: Any, table_name: str) -> str:
        """解析表注释"""
        row = result.fetchone()
        if not row or not row[0]:
            return ""

        create_sql = row[0]
        # 从创建语句中提取注释（SQLite 的注释通常在特定位置）
        if "/*" in create_sql and "*/" in create_sql:
            comment_match = re.search(r"/\*\s*(.*?)\s*\*/", create_sql)
            if comment_match:
                return comment_match.group(1)
        return ""

    def get_system_databases(self) -> set:
        """获取系统数据库集合（SQLite 无系统数据库）"""
        return set()

    def show_databases(self) -> Dict[str, Any]:
        """
        显示数据库列表（SQLite 返回当前数据库信息）

        Returns:
            Dict[str, Any]: 包含数据库信息的字典
        """
        db_path = self.config.get("database", "database.db")
        return {
            "message": "SQLite 使用单文件数据库，不支持列出多个数据库",
            "db_type": "sqlite",
            "current_database": db_path,
            "total_count": 1,
            "user_databases": [db_path],
            "all_databases": [db_path],
            "system_databases": [],
        }
