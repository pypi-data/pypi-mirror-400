"""
SQLAlchemy MCP Server
提供数据库操作功能的 MCP 服务器
"""

from .utils import get_version

__version__ = get_version()
__author__ = "ferock"
__email__ = "ferock@gmail.com"

from .server import mcp, run_stdio
from .tools import (
    show_databases,
    get_database_info,
    test_database_connection,
    show_tables,
    exec_query
)
from .utils import get_database_config, create_connection_string, get_version

__all__ = [
    "mcp",
    "run_stdio",
    "show_databases",
    "get_database_info",
    "test_database_connection",
    "show_tables",
    "exec_query",
    "get_database_config",
    "create_connection_string",
    "get_version"
]