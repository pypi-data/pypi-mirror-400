"""
关闭 SSH 隧道
"""

import logging
import os
from typing import Dict, Any

from .. import ssh_tunnel_manager

logger = logging.getLogger(__name__)


def stop_ssh_tunnel() -> Dict[str, Any]:
    """
    关闭 SSH 隧道

    停止当前活跃的 SSH 隧道连接，释放相关资源。

    Returns:
        Dict[str, Any]: 包含关闭结果的字典对象

    Example:
        stop_ssh_tunnel()

    Note:
        - 关闭隧道后，之前通过隧道建立的数据库连接将不再可用
        - 建议在关闭隧道前先关闭所有数据库连接
    """
    try:
        tunnel = ssh_tunnel_manager.get_tunnel()
        engine = ssh_tunnel_manager.get_engine()
        tunnel_was_active = tunnel is not None

        # 关闭数据库引擎
        if engine is not None:
            try:
                engine.dispose()
                logger.info("SSH 隧道数据库引擎已关闭")
            except Exception as e:
                logger.warning(f"关闭数据库引擎时出错: {e}")
            ssh_tunnel_manager.clear_engine()

        # 关闭 SSH 隧道
        if tunnel is not None:
            try:
                tunnel.stop()
                logger.info("SSH 隧道已关闭")
            except Exception as e:
                logger.warning(f"关闭 SSH 隧道时出错: {e}")
            ssh_tunnel_manager.clear_tunnel()

        # 清除 SSH 相关环境变量
        ssh_env_vars = ['DB_SSH_TUNNEL', 'DB_SSH_HOST', 'DB_SSH_PORT']
        for var in ssh_env_vars:
            if var in os.environ:
                del os.environ[var]

        if tunnel_was_active:
            return {
                "message": "SSH 隧道已成功关闭",
                "success": True,
                "tunnel_closed": True
            }
        else:
            return {
                "message": "没有活跃的 SSH 隧道需要关闭",
                "success": True,
                "tunnel_closed": False
            }

    except Exception as e:
        logger.error(f"关闭 SSH 隧道失败: {e}")
        return {
            "message": f"关闭 SSH 隧道失败: {str(e)}",
            "success": False,
            "error": True,
            "error_type": "Exception"
        }
