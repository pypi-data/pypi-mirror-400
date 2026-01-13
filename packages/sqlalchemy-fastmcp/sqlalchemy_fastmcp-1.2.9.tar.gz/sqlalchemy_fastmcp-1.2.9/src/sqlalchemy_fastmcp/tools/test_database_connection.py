"""
测试数据库连接功能
"""

import logging
import json
import time
from typing import Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from ..utils import get_database_config, create_connection_string

logger = logging.getLogger(__name__)

def test_database_connection() -> Dict[str, Any]:
    """
    测试数据库连接

    尝试连接到配置的数据库服务器，验证连接是否正常。

    Returns:
        Dict[str, Any]: 包含连接测试结果的字典对象

    Raises:
        SQLAlchemyError: 当数据库连接失败时
        Exception: 当其他操作失败时

    Example:
        test_database_connection()

    Note:
        使用 .env 文件中的配置进行连接测试
    """
    try:
        start_time = time.time()

        # 获取数据库配置
        config = get_database_config()

        # 创建连接字符串
        connection_string = create_connection_string(config)

        # 创建引擎并测试连接
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            # 获取服务器信息
            result = connection.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]

            connection_time = time.time() - start_time

            result_data = {
                "message": "数据库连接测试成功",
                "connected": True,
                "server_info": {
                    "version": version,
                    "host": config['host'],
                    "port": config['port'],
                    "user": config['user'],
                    "database_type": config['db_type']
                },
                "connection_time": round(connection_time, 3)
            }

            return result_data

    except SQLAlchemyError as e:
        logger.error(f"数据库连接测试失败: {e}")
        error_result = {
            "message": f"数据库连接测试失败: {str(e)}",
            "connected": False,
            "error": True,
            "error_type": "SQLAlchemyError"
        }
        return error_result
    except Exception as e:
        logger.error(f"连接测试未知错误: {e}")
        error_result = {
            "message": f"连接测试失败: {str(e)}",
            "connected": False,
            "error": True,
            "error_type": "Exception"
        }
        return error_result
