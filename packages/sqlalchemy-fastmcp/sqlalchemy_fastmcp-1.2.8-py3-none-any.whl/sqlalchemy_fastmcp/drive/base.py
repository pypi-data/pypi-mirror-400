"""
数据库驱动基类
定义所有数据库驱动必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection


class BaseDriver(ABC):
    """数据库驱动基类"""

    def __init__(self, config: Dict[str, str]):
        """
        初始化驱动

        Args:
            config: 数据库配置字典
        """
        self.config = config
        self._engine = None

    @property
    @abstractmethod
    def db_type(self) -> str:
        """返回数据库类型标识"""
        pass

    @property
    @abstractmethod
    def default_port(self) -> int:
        """返回默认端口"""
        pass

    @abstractmethod
    def create_connection_string(self) -> str:
        """
        创建数据库连接字符串

        Returns:
            str: SQLAlchemy 连接字符串
        """
        pass

    @abstractmethod
    def get_show_databases_sql(self) -> str:
        """
        获取显示数据库列表的 SQL 语句

        Returns:
            str: SQL 查询语句
        """
        pass

    @abstractmethod
    def get_show_tables_sql(self) -> str:
        """
        获取显示表列表的 SQL 语句

        Returns:
            str: SQL 查询语句
        """
        pass

    @abstractmethod
    def get_table_comment_sql(self, table_name: str) -> str:
        """
        获取获取表注释的 SQL 语句

        Args:
            table_name: 表名

        Returns:
            str: SQL 查询语句
        """
        pass

    @abstractmethod
    def parse_table_comment(self, result: Any, table_name: str) -> str:
        """
        解析表注释查询结果

        Args:
            result: 查询结果
            table_name: 表名

        Returns:
            str: 表注释
        """
        pass

    @abstractmethod
    def get_system_databases(self) -> set:
        """
        获取系统数据库集合

        Returns:
            set: 系统数据库名称集合
        """
        pass

    def create_engine(self):
        """
        创建 SQLAlchemy 引擎

        Returns:
            Engine: SQLAlchemy 引擎实例
        """
        if self._engine is None:
            connection_string = self.create_connection_string()
            self._engine = create_engine(connection_string)
        return self._engine

    def get_connection(self) -> Connection:
        """
        获取数据库连接

        Returns:
            Connection: SQLAlchemy 连接实例
        """
        engine = self.create_engine()
        return engine.connect()

    def show_databases(self) -> Dict[str, Any]:
        """
        显示数据库列表

        Returns:
            Dict[str, Any]: 包含数据库列表的字典
        """
        connection = self.get_connection()
        try:
            result = connection.execute(text(self.get_show_databases_sql()))
            databases = [row[0] for row in result.fetchall()]

            # 过滤系统数据库
            system_dbs = self.get_system_databases()
            user_databases = [db for db in databases if db not in system_dbs]

            return {
                "message": "成功获取数据库列表",
                "total_count": len(databases),
                "user_databases": user_databases,
                "all_databases": databases,
                "system_databases": list(system_dbs.intersection(set(databases))),
            }
        finally:
            connection.close()

    def show_tables(
        self, page: int = 1, page_size: int = 20, table_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        显示表列表（支持分页）

        Args:
            page: 页码
            page_size: 每页数量
            table_name: 表名筛选

        Returns:
            Dict[str, Any]: 包含表列表的字典
        """
        connection = self.get_connection()
        try:
            result = connection.execute(text(self.get_show_tables_sql()))
            all_tables = [row[0] for row in result.fetchall()]

            # 筛选表名
            if table_name:
                all_tables = [t for t in all_tables if table_name.lower() in t.lower()]

            # 计算分页
            total_tables = len(all_tables)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_tables = all_tables[start_idx:end_idx]
            total_pages = (total_tables + page_size - 1) // page_size

            # 获取表注释
            tables_info = []
            for name in paginated_tables:
                try:
                    comment_result = connection.execute(
                        text(self.get_table_comment_sql(name))
                    )
                    comment = self.parse_table_comment(comment_result, name)
                    tables_info.append({"table_name": name, "table_comment": comment})
                except Exception:
                    tables_info.append({"table_name": name, "table_comment": ""})

            return {
                "message": f"第 {page} / {total_pages} 页，共 {total_tables} 个表",
                "database": self.config.get("database", "default"),
                "total_tables": total_tables,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "tables": tables_info,
                "table_name_filter": table_name,
            }
        finally:
            connection.close()
