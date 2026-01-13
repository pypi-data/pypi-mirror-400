"""
获取数据库配置信息功能
"""

import os
import logging
import json
from typing import Dict, Any
from ..utils import get_database_config

logger = logging.getLogger(__name__)

def get_database_info() -> Dict[str, Any]:
    """
    获取当前数据库配置信息

    读取 .env 文件中的数据库配置，返回配置信息（密码会被隐藏）。

    Returns:
        Dict[str, Any]: 包含数据库配置信息的字典对象

    Raises:
        Exception: 当获取配置信息失败时

    Example:
        get_database_info()

    Note:
        配置信息从 .env 文件读取，包括：
        - DB_HOST: 数据库地址
        - DB_PORT: 数据库端口
        - DB_USER: 数据库用户名
        - DB_PASS: 数据库密码（显示时会被隐藏）
        - DB_TYPE: 数据库类型
        - DB_CHARSET: 数据库编码
    """
    try:
        config = get_database_config()

        # 隐藏密码
        safe_config = config.copy()
        if safe_config['password']:
            safe_config['password'] = '***'

        result_data = {
            "message": "成功获取数据库配置信息",
            "config": safe_config,
            "env_file_exists": os.path.exists('.env')
        }

        return result_data

    except Exception as e:
        logger.error(f"获取配置信息失败: {e}")
        error_result = {
            "message": f"获取配置信息失败: {str(e)}",
            "error": True
        }
        return error_result
