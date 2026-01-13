"""
SQLAlchemy MCP Server
提供数据库操作功能的 MCP 服务器
"""

import logging
import os
from typing import Any, List, Dict, Optional
from mcp.server.fastmcp import FastMCP

# 导入功能模块
from sqlalchemy_fastmcp.tools import (
    show_databases,
    get_database_info,
    test_database_connection,
    show_tables,
    exec_query,
    set_database_source,
    reset_database_source,
    get_current_database_source,
    set_database_source_on_ssh,
    stop_ssh_tunnel,
    get_ssh_tunnel_status,
)

# 获取项目根目录路径用于日志文件路径
# 当使用 stdio 传输方法时，相对路径可能由于客户端的运行位置和权限问题
# 导致日志文件无法创建，从而使程序无法运行。
# 因此使用 os.path.join(ROOT_DIR, "sqlalchemy-mcp.log") 代替

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_FILE = os.path.join(ROOT_DIR, "sqlalchemy-mcp.log")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # 参考 https://github.com/modelcontextprotocol/python-sdk/issues/409#issuecomment-2816831318
        # stdio 模式的服务器绝不能向 stdout 写入任何不是有效 MCP 消息的内容。
        logging.FileHandler(LOG_FILE)
    ],
)
logger = logging.getLogger("sqlalchemy-mcp")

# 初始化 FastMCP 服务器
mcp = FastMCP("sqlalchemy-mcp")


@mcp.tool()
def show_databases_tool() -> Dict[str, Any]:
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
        show_databases_tool()

    Note:
        支持的数据库类型：
        - MySQL: 需要配置 DB_HOST, DB_PORT(默认3306), DB_USER, DB_PASS
        - PostgreSQL: 需要配置 DB_HOST, DB_PORT(默认5432), DB_USER, DB_PASS
        - SQLite: 需要配置 DB_NAME(数据库文件路径)

        环境变量配置：
        - DB_TYPE: 数据库类型（mysql/postgresql/sqlite）
        - DB_HOST: 数据库地址（MySQL/PostgreSQL）
        - DB_PORT: 数据库端口
        - DB_USER: 数据库用户名（MySQL/PostgreSQL）
        - DB_PASS: 数据库密码（MySQL/PostgreSQL）
        - DB_NAME: 数据库名称或文件路径
        - DB_CHARSET: 数据库编码（可选，仅 MySQL）
    """
    try:
        return show_databases()
    except Exception as e:
        logger.error(f"Error showing databases: {e}")
        raise


@mcp.tool()
def get_database_info_tool() -> Dict[str, Any]:
    """
    获取当前数据库配置信息

    读取 .env 文件中的数据库配置，返回配置信息（密码会被隐藏）。

    Returns:
        Dict[str, Any]: 包含数据库配置信息的字典对象

    Raises:
        Exception: 当获取配置信息失败时

    Example:
        get_database_info_tool()

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
        return get_database_info()
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        raise


@mcp.tool()
def test_database_connection_tool() -> Dict[str, Any]:
    """
    测试数据库连接

    尝试连接到配置的数据库服务器，验证连接是否正常。

    Returns:
        Dict[str, Any]: 包含连接测试结果的字典对象

    Raises:
        SQLAlchemyError: 当数据库连接失败时
        Exception: 当其他操作失败时

    Example:
        test_database_connection_tool()

    Note:
        使用 .env 文件中的配置进行连接测试
    """
    try:
        return test_database_connection()
    except Exception as e:
        logger.error(f"Error testing database connection: {e}")
        raise


@mcp.tool()
def show_tables_tool(
    database_name: str = None,
    page: int = 1,
    page_size: int = 20,
    table_name: str = None,
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
        show_tables_tool("my_database", page=1, page_size=20)
        show_tables_tool("my_database", page=2, page_size=10, table_name="user")

    Note:
        支持的数据库类型：
        - MySQL: 需要配置 DB_HOST, DB_PORT(默认3306), DB_USER, DB_PASS
        - PostgreSQL: 需要配置 DB_HOST, DB_PORT(默认5432), DB_USER, DB_PASS
        - SQLite: 需要配置 DB_NAME(数据库文件路径)

        环境变量配置：
        - DB_TYPE: 数据库类型（mysql/postgresql/sqlite）
        - DB_HOST: 数据库地址（MySQL/PostgreSQL）
        - DB_PORT: 数据库端口
        - DB_USER: 数据库用户名（MySQL/PostgreSQL）
        - DB_PASS: 数据库密码（MySQL/PostgreSQL）
        - DB_NAME: 数据库名称或文件路径
        - DB_CHARSET: 数据库编码（可选，仅 MySQL）

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
        return show_tables(database_name, page, page_size, table_name)
    except Exception as e:
        logger.error(f"Error showing tables: {e}")
        raise


@mcp.tool()
def exec_query_tool(
    sql_query: str, database_name: str = None, limit: int = 100
) -> Dict[str, Any]:
    """
    执行 SQL 查询

    连接到指定的数据库，执行 SQL 查询并返回结果。
    支持 MySQL、PostgreSQL 和 SQLite 数据库，自动限制结果数量以防止内存溢出。
    支持通过环境变量控制SQL操作权限，可以禁用INSERT、UPDATE、DELETE操作。

    Args:
        sql_query: 要执行的 SQL 查询语句
        database_name: 数据库名称，如果为 None 则使用配置中的默认数据库
        limit: 结果限制数量，默认 100 行

    Returns:
        Dict[str, Any]: 包含查询结果的字典对象

    Raises:
        SQLAlchemyError: 当数据库连接失败时
        PermissionDenied: 当SQL操作被权限控制拒绝时
        Exception: 当其他操作失败时

    Example:
        exec_query_tool("SELECT * FROM users LIMIT 10", "my_database")

    Note:
        支持的数据库类型：
        - MySQL: 需要配置 DB_HOST, DB_PORT(默认3306), DB_USER, DB_PASS
        - PostgreSQL: 需要配置 DB_HOST, DB_PORT(默认5432), DB_USER, DB_PASS
        - SQLite: 需要配置 DB_NAME(数据库文件路径)

        环境变量配置：
        - DB_TYPE: 数据库类型（mysql/postgresql/sqlite）
        - DB_HOST: 数据库地址（MySQL/PostgreSQL）
        - DB_PORT: 数据库端口
        - DB_USER: 数据库用户名（MySQL/PostgreSQL）
        - DB_PASS: 数据库密码（MySQL/PostgreSQL）
        - DB_NAME: 数据库名称或文件路径
        - DB_CHARSET: 数据库编码（可选，仅 MySQL）

        权限控制环境变量（可选，默认为false）：
        - ALLOW_INSERT_OPERATION: 是否允许INSERT操作（true/false）
        - ALLOW_UPDATE_OPERATION: 是否允许UPDATE/ALTER操作（true/false）
        - ALLOW_DELETE_OPERATION: 是否允许DELETE/DROP操作（true/false）
    """
    try:
        return exec_query(sql_query, database_name, limit)
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        raise


@mcp.tool()
def set_database_source_tool(
    db_type: str = "mysql",
    db_host: str = "localhost",
    db_port: int = 3306,
    db_username: str = "root",
    db_password: str = "",
    db_database_name: str = "",
    db_charset: str = "utf8mb4",
    db_path: str = "",
) -> Dict[str, Any]:
    """
    设置数据库数据源

    动态切换数据库连接配置，支持连接到不同的数据库服务器。
    设置成功后，所有后续的数据库操作都将使用新的配置。

    Args:
        db_type: 数据库类型，支持 mysql、postgresql 和 sqlite
        db_host: 数据库地址（MySQL/PostgreSQL 使用）
        db_port: 数据库端口（MySQL 默认3306，PostgreSQL 默认5432）
        db_username: 数据库用户名（MySQL/PostgreSQL 使用）
        db_password: 数据库密码（MySQL/PostgreSQL 使用）
        db_database_name: 数据库名称（MySQL/PostgreSQL 使用，可选）
        db_charset: 数据库编码（MySQL 使用），默认 utf8mb4
        db_path: 数据库文件路径（SQLite 使用）

    Returns:
        Dict[str, Any]: 包含设置结果的字典对象

    Raises:
        ValueError: 当数据库类型不支持时
        SQLAlchemyError: 当数据库连接测试失败时
        Exception: 当其他操作失败时

    Example:
        # MySQL 示例
        set_database_source_tool(
            db_type="mysql",
            db_host="192.168.1.100",
            db_port=3306,
            db_username="admin",
            db_password="password123",
            db_database_name="test_db",
            db_charset="utf8mb4"
        )

        # PostgreSQL 示例
        set_database_source_tool(
            db_type="postgresql",
            db_host="192.168.1.100",
            db_port=5432,
            db_username="postgres",
            db_password="password123",
            db_database_name="test_db"
        )

        # SQLite 示例
        set_database_source_tool(
            db_type="sqlite",
            db_path="/path/to/database.db"
        )

    Note:
        - 支持 MySQL、PostgreSQL 和 SQLite 数据库
        - 设置成功后会自动测试连接
        - 新配置会覆盖环境变量中的配置
        - 配置仅在当前会话中有效，重启后恢复环境变量配置
        - SQLite 使用 db_path 参数指定数据库文件路径
    """
    try:
        return set_database_source(
            db_type=db_type,
            db_host=db_host,
            db_port=db_port,
            db_username=db_username,
            db_password=db_password,
            db_database_name=db_database_name,
            db_charset=db_charset,
            db_path=db_path,
        )
    except Exception as e:
        logger.error(f"Error setting database source: {e}")
        raise


@mcp.tool()
def reset_database_source_tool() -> Dict[str, Any]:
    """
    重置数据库数据源到环境变量配置

    将数据库配置重置为环境变量中的配置，取消之前通过 set_database_source_tool 设置的动态配置。

    Returns:
        Dict[str, Any]: 包含重置结果的字典对象

    Raises:
        Exception: 当重置操作失败时

    Example:
        reset_database_source_tool()

    Note:
        重置后，所有数据库操作将使用环境变量中的配置
    """
    try:
        return reset_database_source()
    except Exception as e:
        logger.error(f"Error resetting database source: {e}")
        raise


@mcp.tool()
def get_current_database_source_tool() -> Dict[str, Any]:
    """
    获取当前数据库数据源配置

    读取当前环境变量中的数据库配置信息，显示当前正在使用的数据源。

    Returns:
        Dict[str, Any]: 包含当前数据库配置的字典对象

    Raises:
        Exception: 当获取配置失败时

    Example:
        get_current_database_source_tool()

    Note:
        返回的配置信息中，密码会被隐藏显示
        同时显示环境变量的原始值用于调试
    """
    try:
        return get_current_database_source()
    except Exception as e:
        logger.error(f"Error getting current database source: {e}")
        raise


@mcp.tool()
def set_database_source_on_ssh_tool(
    ssh_hostname: str,
    ssh_username: str,
    ssh_password: str = "",
    ssh_passkey: str = "",
    ssh_port: int = 22,
    db_type: str = "mysql",
    db_host: str = "127.0.0.1",
    db_port: int = 3306,
    db_username: str = "root",
    db_password: str = "",
    db_database_name: str = "",
    db_charset: str = "utf8mb4",
) -> Dict[str, Any]:
    """
    通过 SSH 隧道设置数据库数据源

    使用 SSH 隧道安全连接远程数据库服务器。所有数据库流量将通过 SSH 隧道加密传输。
    支持密码和密钥两种认证方式，如果同时提供则优先尝试密钥认证，失败后尝试密码认证。

    Args:
        ssh_hostname: SSH 服务器地址
        ssh_username: SSH 登录用户名
        ssh_password: SSH 登录密码（与 ssh_passkey 二选一，或同时提供）
        ssh_passkey: SSH 私钥文件路径（与 ssh_password 二选一，或同时提供）
        ssh_port: SSH 端口，默认 22
        db_type: 数据库类型，支持 mysql 和 postgresql
        db_host: 远程服务器上数据库的地址，通常是 127.0.0.1
        db_port: 数据库端口，MySQL 默认3306，PostgreSQL 默认5432
        db_username: 数据库用户名
        db_password: 数据库密码
        db_database_name: 数据库名称
        db_charset: 数据库编码（仅 MySQL 使用），默认 utf8mb4

    Returns:
        Dict[str, Any]: 包含设置结果的字典对象

    Raises:
        ValueError: 当参数不正确或认证失败时
        SQLAlchemyError: 当数据库连接测试失败时
        Exception: 当其他操作失败时

    Example:
        # 使用密码认证连接 MySQL
        set_database_source_on_ssh_tool(
            ssh_hostname="192.168.1.100",
            ssh_username="ubuntu",
            ssh_password="ssh_password",
            ssh_port=22,
            db_type="mysql",
            db_host="127.0.0.1",
            db_port=3306,
            db_username="root",
            db_password="db_password",
            db_database_name="mydb"
        )

        # 使用密钥认证连接 PostgreSQL
        set_database_source_on_ssh_tool(
            ssh_hostname="192.168.1.100",
            ssh_username="ubuntu",
            ssh_passkey="/home/user/.ssh/id_rsa",
            ssh_port=22,
            db_type="postgresql",
            db_host="127.0.0.1",
            db_port=5432,
            db_username="postgres",
            db_password="db_password",
            db_database_name="mydb"
        )

    Note:
        - 使用长连接模式，隧道在 MCP 服务运行期间保持开启
        - 设置新的 SSH 隧道会自动关闭之前的隧道
        - 使用 pool_recycle=3600 防止连接超时
        - 如果同时提供密钥和密码，优先尝试密钥认证，失败后尝试密码认证
    """
    try:
        return set_database_source_on_ssh(
            ssh_hostname=ssh_hostname,
            ssh_username=ssh_username,
            ssh_password=ssh_password,
            ssh_passkey=ssh_passkey,
            ssh_port=ssh_port,
            db_type=db_type,
            db_host=db_host,
            db_port=db_port,
            db_username=db_username,
            db_password=db_password,
            db_database_name=db_database_name,
            db_charset=db_charset,
        )
    except Exception as e:
        logger.error(f"Error setting database source on SSH: {e}")
        raise


@mcp.tool()
def stop_ssh_tunnel_tool() -> Dict[str, Any]:
    """
    关闭 SSH 隧道

    停止当前活跃的 SSH 隧道连接，释放相关资源。

    Returns:
        Dict[str, Any]: 包含关闭结果的字典对象

    Raises:
        Exception: 当关闭操作失败时

    Example:
        stop_ssh_tunnel_tool()

    Note:
        - 关闭隧道后，之前通过隧道建立的数据库连接将不再可用
        - 建议在关闭隧道前先关闭所有数据库连接
    """
    try:
        return stop_ssh_tunnel()
    except Exception as e:
        logger.error(f"Error stopping SSH tunnel: {e}")
        raise


@mcp.tool()
def get_ssh_tunnel_status_tool() -> Dict[str, Any]:
    """
    获取 SSH 隧道状态

    返回当前 SSH 隧道的连接状态信息。

    Returns:
        Dict[str, Any]: 包含隧道状态的字典对象

    Raises:
        Exception: 当获取状态失败时

    Example:
        get_ssh_tunnel_status_tool()

    Note:
        返回信息包括隧道是否活跃、本地绑定端口、SSH 服务器地址等
    """
    try:
        return get_ssh_tunnel_status()
    except Exception as e:
        logger.error(f"Error getting SSH tunnel status: {e}")
        raise


async def run_sse():
    """运行 SQLAlchemy MCP 服务器在 SSE 模式"""
    try:
        logger.info("启动 SQLAlchemy MCP 服务器 (SSE 模式)")
        await mcp.run_sse_async()
    except KeyboardInterrupt:
        logger.info("服务器被用户停止")
    except Exception as e:
        logger.error(f"服务器失败: {e}")
        raise
    finally:
        logger.info("服务器关闭完成")


async def run_streamable_http():
    """运行 SQLAlchemy MCP 服务器在 streamable HTTP 模式"""
    try:
        logger.info("启动 SQLAlchemy MCP 服务器 (streamable HTTP 模式)")
        await mcp.run_streamable_http_async()
    except KeyboardInterrupt:
        logger.info("服务器被用户停止")
    except Exception as e:
        logger.error(f"服务器失败: {e}")
        raise
    finally:
        logger.info("服务器关闭完成")


def run_stdio():
    """运行 SQLAlchemy MCP 服务器在 stdio 模式"""
    try:
        logger.info("启动 SQLAlchemy MCP 服务器 (stdio 模式)")
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("服务器被用户停止")
    except Exception as e:
        logger.error(f"服务器失败: {e}")
        raise
    finally:
        logger.info("服务器关闭完成")


def main():
    """主入口函数"""
    mcp.run()


if __name__ == "__main__":
    main()
