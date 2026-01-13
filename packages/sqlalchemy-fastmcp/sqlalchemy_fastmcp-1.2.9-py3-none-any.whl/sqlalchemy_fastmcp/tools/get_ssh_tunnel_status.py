"""
获取 SSH 隧道状态
"""

import logging
import os
from typing import Dict, Any

from .. import ssh_tunnel_manager

logger = logging.getLogger(__name__)


def get_ssh_tunnel_status() -> Dict[str, Any]:
    """
    获取 SSH 隧道状态

    返回当前 SSH 隧道的连接状态信息。

    Returns:
        Dict[str, Any]: 包含隧道状态的字典对象

    Example:
        get_ssh_tunnel_status()
    """
    try:
        tunnel = ssh_tunnel_manager.get_tunnel()

        if tunnel is None:
            return {
                "message": "当前没有活跃的 SSH 隧道",
                "success": True,
                "tunnel_active": False
            }

        is_alive = tunnel.is_alive if hasattr(tunnel, 'is_alive') else False

        return {
            "message": "SSH 隧道状态",
            "success": True,
            "tunnel_active": True,
            "is_alive": is_alive,
            "local_bind_port": tunnel.local_bind_port if hasattr(tunnel, 'local_bind_port') else None,
            "ssh_host": os.environ.get('DB_SSH_HOST', '未知'),
            "ssh_port": os.environ.get('DB_SSH_PORT', '未知')
        }

    except Exception as e:
        logger.error(f"获取 SSH 隧道状态失败: {e}")
        return {
            "message": f"获取 SSH 隧道状态失败: {str(e)}",
            "success": False,
            "error": True,
            "error_type": "Exception"
        }
