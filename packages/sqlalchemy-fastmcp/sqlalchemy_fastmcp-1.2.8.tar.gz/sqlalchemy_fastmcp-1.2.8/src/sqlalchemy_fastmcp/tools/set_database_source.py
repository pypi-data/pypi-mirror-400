"""
设置数据库数据源功能
"""

import logging
import json
import os
from typing import Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from ..utils import create_connection_string, get_database_config

logger = logging.getLogger(__name__)

def set_database_source(
    db_type: str = "mysql",
    db_host: str = "localhost",
    db_port: int = 3306,
    db_username: str = "root",
    db_password: str = "",
    db_database_name: str = "",
    db_charset: str = "utf8mb4",
    db_path: str = ""
) -> Dict[str, Any]:
    """
    设置数据库数据源

    通过修改环境变量来切换数据库连接配置，支持连接到不同的数据库服务器。
    设置成功后，所有后续的数据库操作都将使用新的环境变量配置。

    Args:
        db_type: 数据库类型，支持 mysql 和 sqlite
        db_host: 数据库地址（MySQL 使用）
        db_port: 数据库端口（MySQL 使用）
        db_username: 数据库用户名（MySQL 使用）
        db_password: 数据库密码（MySQL 使用）
        db_database_name: 数据库名称（MySQL 使用，可选）
        db_charset: 数据库编码（MySQL 使用），默认 utf8mb4
        db_path: 数据库文件路径（SQLite 使用）

    Returns:
        Dict[str, Any]: 包含设置结果的字典对象

    Raises:
        ValueError: 当数据库类型不支持时
        SQLAlchemyError: 当数据库连接测试失败时
        Exception: 当其他操作失败时

    Example:
        set_database_source(
            db_type="mysql",
            db_host="192.168.1.100",
            db_port=3306,
            db_username="admin",
            db_password="password123",
            db_database_name="test_db",
            db_charset="utf8mb4"
        )

    Note:
        - 支持 MySQL 和 SQLite 数据库
        - 设置成功后会自动测试连接
        - 新配置会修改当前进程的环境变量
        - 配置在当前会话中有效，重启后需要重新设置
        - SQLite 使用 db_path 参数指定数据库文件路径
    """
    try:
        # 验证数据库类型
        if db_type.lower() not in ["mysql", "sqlite"]:
            error_result = {
                "message": f"不支持的数据库类型: {db_type}，支持 mysql 和 sqlite",
                "success": False,
                "error": True,
                "error_type": "ValueError"
            }
            return error_result

        # 构建新的数据库配置
        if db_type.lower() == 'sqlite':
            # SQLite 配置
            new_config = {
                'host': '',
                'port': '',
                'user': '',
                'password': '',
                'database': db_path if db_path else db_database_name,
                'charset': '',
                'db_type': 'sqlite'
            }
        else:
            # MySQL 配置
            new_config = {
                'host': db_host,
                'port': str(db_port),
                'user': db_username,
                'password': db_password,
                'database': db_database_name,
                'charset': db_charset,
                'db_type': db_type.lower()
            }

        logger.info(f"尝试设置新的数据库配置: {dict(new_config, password='***')}")

        # 测试新配置的连接
        connection_string = create_connection_string(new_config)
        engine = create_engine(connection_string)

        # 测试连接并获取服务器信息
        with engine.connect() as connection:
            if db_type.lower() == 'sqlite':
                result = connection.execute(text("SELECT sqlite_version()"))
                version = f"SQLite {result.fetchone()[0]}"
            else:
                result = connection.execute(text("SELECT VERSION()"))
                version = result.fetchone()[0]

            # 连接成功，更新环境变量
            if db_type.lower() == 'sqlite':
                os.environ['DB_TYPE'] = 'sqlite'
                os.environ['DB_NAME'] = db_path if db_path else db_database_name
                # 清除 MySQL 相关的环境变量
                for key in ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASS', 'DB_CHARSET']:
                    if key in os.environ:
                        del os.environ[key]
            else:
                os.environ['DB_HOST'] = db_host
                os.environ['DB_PORT'] = str(db_port)
                os.environ['DB_USER'] = db_username
                os.environ['DB_PASS'] = db_password
                os.environ['DB_NAME'] = db_database_name
                os.environ['DB_CHARSET'] = db_charset
                os.environ['DB_TYPE'] = db_type.lower()

            result_data = {
                "message": "数据库数据源设置成功，环境变量已更新",
                "success": True,
                "config": {
                    "db_type": new_config['db_type'],
                    "host": new_config['host'],
                    "port": new_config['port'],
                    "user": new_config['user'],
                    "database": new_config['database'],
                    "charset": new_config['charset']
                },
                "server_info": {
                    "version": version,
                    "connection_test": "成功"
                },
                "environment_variables_updated": [
                    "DB_HOST", "DB_PORT", "DB_USER", "DB_PASS",
                    "DB_NAME", "DB_CHARSET", "DB_TYPE"
                ]
            }

            logger.info(f"数据库数据源设置成功，环境变量已更新: {new_config['host']}:{new_config['port']}")
            return result_data

    except SQLAlchemyError as e:
        logger.error(f"数据库连接测试失败: {e}")
        error_result = {
            "message": f"数据库连接测试失败: {str(e)}",
            "success": False,
            "error": True,
            "error_type": "SQLAlchemyError",
            "config": {
                "db_type": db_type,
                "host": db_host,
                "port": db_port,
                "user": db_username,
                "database": db_database_name,
                "charset": db_charset
            }
        }
        return error_result

    except Exception as e:
        logger.error(f"设置数据库数据源失败: {e}")
        # 检查是否是依赖缺失错误
        error_message = str(e)
        if "No module named 'pymysql'" in error_message:
            error_message = "缺少必要的依赖包 pymysql，请安装: pip install pymysql"

        error_result = {
            "message": f"设置数据库数据源失败: {error_message}",
            "success": False,
            "error": True,
            "error_type": "Exception",
            "config": {
                "db_type": db_type,
                "host": db_host,
                "port": db_port,
                "user": db_username,
                "database": db_database_name,
                "charset": db_charset
            }
        }
        return error_result

def get_current_database_source() -> Dict[str, Any]:
    """
    获取当前数据库数据源配置

    读取当前环境变量中的数据库配置信息。

    Returns:
        Dict[str, Any]: 包含当前数据库配置的字典对象

    Example:
        get_current_database_source()

    Note:
        返回的配置信息中，密码会被隐藏显示
    """
    try:
        config = get_database_config()

        # 隐藏密码
        display_config = config.copy()
        if display_config['password']:
            display_config['password'] = '*' * len(display_config['password'])

        result_data = {
            "message": "当前数据库数据源配置",
            "success": True,
            "config": {
                "db_type": display_config['db_type'],
                "host": display_config['host'],
                "port": display_config['port'],
                "user": display_config['user'],
                "database": display_config['database'],
                "charset": display_config['charset'],
                "password": display_config['password']
            },
            "environment_variables": {
                "DB_HOST": os.getenv('DB_HOST', '未设置'),
                "DB_PORT": os.getenv('DB_PORT', '未设置'),
                "DB_USER": os.getenv('DB_USER', '未设置'),
                "DB_PASS": "***" if os.getenv('DB_PASS') else '未设置',
                "DB_NAME": os.getenv('DB_NAME', '未设置'),
                "DB_CHARSET": os.getenv('DB_CHARSET', '未设置'),
                "DB_TYPE": os.getenv('DB_TYPE', '未设置')
            }
        }

        logger.info("获取当前数据库数据源配置成功")
        return result_data

    except Exception as e:
        logger.error(f"获取当前数据库数据源配置失败: {e}")
        error_result = {
            "message": f"获取当前数据库数据源配置失败: {str(e)}",
            "success": False,
            "error": True,
            "error_type": "Exception"
        }
        return error_result

def reset_database_source() -> Dict[str, Any]:
    """
    重置数据库数据源到默认配置

    清除当前进程中设置的数据库环境变量，恢复到系统默认配置。

    Returns:
        Dict[str, Any]: 包含重置结果的字典对象

    Example:
        reset_database_source()

    Note:
        重置后，数据库操作将使用系统环境变量或默认配置
    """
    try:
        # 记录重置前的配置
        old_config = get_database_config()

        # 清除当前进程的数据库环境变量
        db_env_vars = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASS', 'DB_NAME', 'DB_CHARSET', 'DB_TYPE']
        cleared_vars = []

        for var in db_env_vars:
            if var in os.environ:
                del os.environ[var]
                cleared_vars.append(var)

        # 获取重置后的配置
        new_config = get_database_config()

        # 隐藏密码
        display_config = new_config.copy()
        if display_config['password']:
            display_config['password'] = '*' * len(display_config['password'])

        result_data = {
            "message": "数据库数据源已重置到默认配置",
            "success": True,
            "config": {
                "db_type": display_config['db_type'],
                "host": display_config['host'],
                "port": display_config['port'],
                "user": display_config['user'],
                "database": display_config['database'],
                "charset": display_config['charset'],
                "password": display_config['password']
            },
            "cleared_environment_variables": cleared_vars
        }

        logger.info(f"数据库数据源已重置，清除了 {len(cleared_vars)} 个环境变量")
        return result_data

    except Exception as e:
        logger.error(f"重置数据库数据源失败: {e}")
        error_result = {
            "message": f"重置数据库数据源失败: {str(e)}",
            "success": False,
            "error": True,
            "error_type": "Exception"
        }
        return error_result

