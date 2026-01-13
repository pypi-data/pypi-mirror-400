"""
显示数据库列表功能
"""

import logging
from typing import Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from ..utils import get_database_driver

logger = logging.getLogger(__name__)


def show_databases() -> Dict[str, Any]:
    """
    显示数据库列表

    连接到配置的数据库服务器，获取所有可用的数据库列表。
    支持 MySQL、PostgreSQL 和 SQLite 数据库，自动过滤系统数据库。

    Returns:
        Dict[str, Any]: 包含数据库列表的字典对象

    Raises:
        SQLAlchemyError: 当数据库连接失败时
        Exception: 当其他操作失败时

    Example:
        show_databases()

    Note:
        需要在 .env 文件中配置数据库连接信息：
        - DB_HOST: 数据库地址
        - DB_PORT: 数据库端口
        - DB_USER: 数据库用户名
        - DB_PASS: 数据库密码
        - DB_TYPE: 数据库类型（mysql、postgresql、sqlite）
        - DB_CHARSET: 数据库编码（可选）
    """
    try:
        driver = get_database_driver()
        logger.info(f"数据库类型: {driver.db_type}")
        return driver.show_databases()
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
