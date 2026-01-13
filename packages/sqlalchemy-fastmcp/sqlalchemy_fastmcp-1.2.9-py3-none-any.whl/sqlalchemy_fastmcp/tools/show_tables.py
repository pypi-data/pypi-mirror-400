"""
显示数据库表列表功能
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from ..utils import get_database_driver

logger = logging.getLogger(__name__)


def show_tables(
    database_name: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    table_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    显示数据库内数据表的列表（支持分页）

    连接到指定的数据库，获取数据表列表，支持分页查询。
    支持 MySQL、PostgreSQL 和 SQLite 数据库，返回表的详细信息。

    Args:
        database_name: 数据库名称，如果为 None 则使用配置中的默认数据库
        page: 页码，默认第 1 页
        page_size: 每页显示数量，默认 20 条
        table_name: 表名筛选（可选），支持模糊匹配

    Returns:
        Dict[str, Any]: 包含表列表的字典对象

    Raises:
        SQLAlchemyError: 当数据库连接失败时
        Exception: 当其他操作失败时

    Example:
        show_tables("my_database", page=1, page_size=20)
        show_tables("my_database", page=2, page_size=10, table_name="user")

    Note:
        需要在 .env 文件中配置数据库连接信息：
        - DB_HOST: 数据库地址
        - DB_PORT: 数据库端口
        - DB_USER: 数据库用户名
        - DB_PASS: 数据库密码
        - DB_TYPE: 数据库类型（mysql、postgresql、sqlite）
        - DB_CHARSET: 数据库编码（可选）

        返回数据包含分页信息：
        - total_tables: 总表数量
        - page: 当前页码
        - page_size: 每页数量
        - total_pages: 总页数
        - tables: 当前页的表信息列表（只包含表名和注释）
        - table_name_filter: 筛选条件

        注意：为了减少响应大小，只返回表名和注释信息。
              如需完整的 DDL 或列信息，请使用 exec_query_tool 执行相应的 SQL 查询。
    """
    try:
        driver = get_database_driver()
        logger.info(f"数据库类型: {driver.db_type}")

        # 如果指定了数据库名称，更新配置
        if database_name:
            driver.config["database"] = database_name

        # 参数校验
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20

        return driver.show_tables(page, page_size, table_name)
    except SQLAlchemyError as e:
        logger.error(f"数据库连接错误: {e}")
        return {
            "message": f"数据库连接失败: {str(e)}",
            "error": True,
            "error_type": "SQLAlchemyError",
        }
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return {
            "message": f"操作失败: {str(e)}",
            "error": True,
            "error_type": "Exception",
        }
