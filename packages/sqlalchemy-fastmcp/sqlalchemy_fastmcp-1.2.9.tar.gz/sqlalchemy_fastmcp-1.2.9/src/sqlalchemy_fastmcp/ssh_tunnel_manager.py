"""
SSH 隧道管理器
管理 SSH 隧道的全局状态和生命周期
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# SSH 隧道管理器（长连接模式）
_ssh_tunnel: Optional[Any] = None
_ssh_engine: Optional[Any] = None


def get_tunnel():
    """获取当前 SSH 隧道实例"""
    global _ssh_tunnel
    return _ssh_tunnel


def set_tunnel(tunnel):
    """设置 SSH 隧道实例"""
    global _ssh_tunnel
    _ssh_tunnel = tunnel


def get_engine():
    """获取当前数据库引擎实例"""
    global _ssh_engine
    return _ssh_engine


def set_engine(engine):
    """设置数据库引擎实例"""
    global _ssh_engine
    _ssh_engine = engine


def clear_tunnel():
    """清除隧道实例"""
    global _ssh_tunnel
    _ssh_tunnel = None


def clear_engine():
    """清除引擎实例"""
    global _ssh_engine
    _ssh_engine = None
