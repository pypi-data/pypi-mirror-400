"""
通过 SSH 隧道设置数据库数据源
"""

import logging
import os
from typing import Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

from .. import ssh_tunnel_manager
from .stop_ssh_tunnel import stop_ssh_tunnel

logger = logging.getLogger(__name__)


def set_database_source_on_ssh(
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
    db_charset: str = "utf8mb4"
) -> Dict[str, Any]:
    """
    通过 SSH 隧道设置数据库数据源

    使用 SSH 隧道安全连接远程数据库服务器。所有数据库流量将通过 SSH 隧道加密传输。
    支持密码和密钥两种认证方式，如果同时提供则优先尝试密钥认证。

    Args:
        ssh_hostname: SSH 服务器地址
        ssh_username: SSH 登录用户名
        ssh_password: SSH 登录密码（与 ssh_passkey 二选一，或同时提供）
        ssh_passkey: SSH 私钥文件路径（与 ssh_password 二选一，或同时提供）
        ssh_port: SSH 端口，默认 22
        db_type: 数据库类型，目前仅支持 mysql
        db_host: 远程服务器上数据库的地址，通常是 127.0.0.1
        db_port: 数据库端口，默认 3306
        db_username: 数据库用户名
        db_password: 数据库密码
        db_database_name: 数据库名称
        db_charset: 数据库编码，默认 utf8mb4

    Returns:
        Dict[str, Any]: 包含设置结果的字典对象

    Raises:
        ValueError: 当参数不正确或认证失败时
        SQLAlchemyError: 当数据库连接测试失败时
        Exception: 当其他操作失败时

    Example:
        # 使用密码认证
        set_database_source_on_ssh(
            ssh_hostname="192.168.1.100",
            ssh_username="ubuntu",
            ssh_password="ssh_password",
            ssh_port=22,
            db_host="127.0.0.1",
            db_port=3306,
            db_username="root",
            db_password="db_password",
            db_database_name="mydb"
        )

        # 使用密钥认证
        set_database_source_on_ssh(
            ssh_hostname="192.168.1.100",
            ssh_username="ubuntu",
            ssh_passkey="/home/user/.ssh/id_rsa",
            ssh_port=22,
            db_host="127.0.0.1",
            db_port=3306,
            db_username="root",
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
        # 验证参数
        if db_type.lower() != "mysql":
            return {
                "message": f"SSH 隧道模式目前仅支持 MySQL 数据库，不支持: {db_type}",
                "success": False,
                "error": True,
                "error_type": "ValueError"
            }

        if not ssh_hostname or not ssh_username:
            return {
                "message": "必须提供 ssh_hostname 和 ssh_username",
                "success": False,
                "error": True,
                "error_type": "ValueError"
            }

        if not ssh_password and not ssh_passkey:
            return {
                "message": "必须提供 ssh_password 或 ssh_passkey 中的至少一项",
                "success": False,
                "error": True,
                "error_type": "ValueError"
            }

        # 尝试导入 sshtunnel
        try:
            from sshtunnel import SSHTunnelForwarder
        except ImportError:
            return {
                "message": "缺少必要的依赖包 sshtunnel，请安装: pip install sshtunnel",
                "success": False,
                "error": True,
                "error_type": "ImportError"
            }

        # 关闭之前的隧道和引擎
        stop_ssh_tunnel()

        logger.info(f"尝试建立 SSH 隧道到 {ssh_hostname}:{ssh_port}")

        # 认证尝试顺序：优先密钥，然后密码
        auth_methods = []
        if ssh_passkey:
            auth_methods.append(("passkey", ssh_passkey))
        if ssh_password:
            auth_methods.append(("password", ssh_password))

        tunnel = None
        last_error = None

        for auth_type, auth_value in auth_methods:
            try:
                if auth_type == "passkey":
                    # 检查密钥文件是否存在
                    if not os.path.exists(auth_value):
                        last_error = f"SSH 密钥文件不存在: {auth_value}"
                        logger.warning(last_error)
                        continue

                    logger.info(f"尝试使用密钥认证: {auth_value}")
                    tunnel = SSHTunnelForwarder(
                        (ssh_hostname, ssh_port),
                        ssh_username=ssh_username,
                        ssh_pkey=auth_value,
                        remote_bind_address=(db_host, db_port),
                        local_bind_address=('127.0.0.1', 0)  # 自动分配本地端口
                    )
                else:  # password
                    logger.info("尝试使用密码认证")
                    tunnel = SSHTunnelForwarder(
                        (ssh_hostname, ssh_port),
                        ssh_username=ssh_username,
                        ssh_password=auth_value,
                        remote_bind_address=(db_host, db_port),
                        local_bind_address=('127.0.0.1', 0)  # 自动分配本地端口
                    )

                # 启动隧道
                tunnel.start()
                logger.info(f"SSH 隧道建立成功，本地端口: {tunnel.local_bind_port}")
                break

            except Exception as e:
                last_error = str(e)
                logger.warning(f"使用 {auth_type} 认证失败: {e}")
                if tunnel:
                    try:
                        tunnel.stop()
                    except Exception:
                        pass
                    tunnel = None
                continue

        if tunnel is None:
            return {
                "message": f"SSH 认证失败，所有认证方式均不成功。最后的错误: {last_error}",
                "success": False,
                "error": True,
                "error_type": "AuthenticationError"
            }

        ssh_tunnel_manager.set_tunnel(tunnel)

        # 通过隧道连接数据库
        local_port = tunnel.local_bind_port

        # 构建连接字符串，使用本地隧道端口
        if db_database_name:
            connection_string = (
                f"mysql+pymysql://{db_username}:{db_password}"
                f"@127.0.0.1:{local_port}/{db_database_name}"
                f"?charset={db_charset}"
            )
        else:
            connection_string = (
                f"mysql+pymysql://{db_username}:{db_password}"
                f"@127.0.0.1:{local_port}"
                f"?charset={db_charset}"
            )

        # 创建引擎，使用连接池并设置 pool_recycle 防止超时
        engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_recycle=3600,  # 每小时回收连接
            pool_pre_ping=True  # 使用前 ping 检查连接是否有效
        )

        # 测试连接
        with engine.connect() as connection:
            result = connection.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]

        ssh_tunnel_manager.set_engine(engine)

        # 更新环境变量，标记为 SSH 隧道模式
        os.environ['DB_HOST'] = '127.0.0.1'
        os.environ['DB_PORT'] = str(local_port)
        os.environ['DB_USER'] = db_username
        os.environ['DB_PASS'] = db_password
        os.environ['DB_NAME'] = db_database_name
        os.environ['DB_CHARSET'] = db_charset
        os.environ['DB_TYPE'] = 'mysql'
        os.environ['DB_SSH_TUNNEL'] = 'true'
        os.environ['DB_SSH_HOST'] = ssh_hostname
        os.environ['DB_SSH_PORT'] = str(ssh_port)

        result_data = {
            "message": "SSH 隧道数据库连接设置成功",
            "success": True,
            "ssh_tunnel": {
                "ssh_host": ssh_hostname,
                "ssh_port": ssh_port,
                "ssh_username": ssh_username,
                "local_bind_port": local_port,
                "remote_bind_address": f"{db_host}:{db_port}"
            },
            "database": {
                "db_type": "mysql",
                "db_host": db_host,
                "db_port": db_port,
                "db_username": db_username,
                "db_database_name": db_database_name,
                "db_charset": db_charset
            },
            "server_info": {
                "version": version,
                "connection_test": "成功"
            },
            "note": "所有数据库流量将通过 SSH 隧道加密传输"
        }

        logger.info(f"SSH 隧道数据库连接设置成功: {ssh_hostname}:{ssh_port} -> {db_host}:{db_port}")
        return result_data

    except SQLAlchemyError as e:
        # 连接失败，清理隧道
        stop_ssh_tunnel()
        logger.error(f"数据库连接测试失败: {e}")
        return {
            "message": f"数据库连接测试失败: {str(e)}",
            "success": False,
            "error": True,
            "error_type": "SQLAlchemyError"
        }

    except Exception as e:
        # 其他错误，清理隧道
        stop_ssh_tunnel()
        logger.error(f"设置 SSH 隧道数据库连接失败: {e}")

        error_message = str(e)
        if "No module named 'pymysql'" in error_message:
            error_message = "缺少必要的依赖包 pymysql，请安装: pip install pymysql"

        return {
            "message": f"设置 SSH 隧道数据库连接失败: {error_message}",
            "success": False,
            "error": True,
            "error_type": "Exception"
        }
