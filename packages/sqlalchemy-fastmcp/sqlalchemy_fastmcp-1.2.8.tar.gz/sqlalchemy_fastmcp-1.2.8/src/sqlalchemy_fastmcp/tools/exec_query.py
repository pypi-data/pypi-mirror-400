"""
执行 SQL 查询功能
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from ..utils import get_database_driver, is_sql_operation_allowed

logger = logging.getLogger(__name__)


def exec_query(
    sql_query: str, database_name: Optional[str] = None, limit: int = 100
) -> Dict[str, Any]:
    """
    执行 SQL 查询

    连接到指定的数据库，执行 SQL 查询并返回结果。
    支持 MySQL、PostgreSQL 和 SQLite 数据库，自动限制结果数量以防止内存溢出。

    Args:
        sql_query: 要执行的 SQL 查询语句
        database_name: 数据库名称，如果为 None 则使用配置中的默认数据库
        limit: 结果限制数量，默认 100 行

    Returns:
        Dict[str, Any]: 包含查询结果的字典对象

    Raises:
        SQLAlchemyError: 当数据库连接失败时
        Exception: 当其他操作失败时

    Example:
        exec_query("SELECT * FROM users LIMIT 10", "my_database")

    Note:
        需要在 .env 文件中配置数据库连接信息：
        - DB_HOST: 数据库地址
        - DB_PORT: 数据库端口
        - DB_USER: 数据库用户名
        - DB_PASS: 数据库密码
        - DB_TYPE: 数据库类型（mysql、postgresql、sqlite）
        - DB_CHARSET: 数据库编码（可选）

        权限控制环境变量（可选，默认为false）：
        - ALLOW_INSERT_OPERATION: 是否允许INSERT操作（true/false）
        - ALLOW_UPDATE_OPERATION: 是否允许UPDATE/ALTER操作（true/false）
        - ALLOW_DELETE_OPERATION: 是否允许DELETE/DROP操作（true/false）
    """
    try:
        # 检查SQL操作权限
        is_allowed, error_message = is_sql_operation_allowed(sql_query)
        if not is_allowed:
            logger.warning(f"SQL操作被拒绝: {error_message}")
            return {
                "message": error_message,
                "error": True,
                "error_type": "PermissionDenied",
                "sql_query": sql_query,
            }

        # 获取数据库驱动
        driver = get_database_driver()
        logger.info(f"数据库类型: {driver.db_type}")

        # 如果指定了数据库名称，更新配置
        if database_name:
            driver.config["database"] = database_name

        # 创建引擎
        engine = driver.create_engine()

        # 连接并执行查询
        with engine.connect() as connection:
            # 检查 SQL 查询是否包含 LIMIT 子句
            sql_upper = sql_query.upper().strip()
            if not sql_upper.endswith("LIMIT") and "LIMIT" not in sql_upper:
                # 如果不是 SELECT 查询，不添加 LIMIT
                if sql_upper.startswith("SELECT"):
                    sql_query = f"{sql_query} LIMIT {limit}"

            logger.info(f"执行 SQL 查询: {sql_query}")

            # 执行查询
            result = connection.execute(text(sql_query))

            # 检查是否为 INSERT/UPDATE/DELETE 操作
            is_dml_operation = any(
                sql_upper.startswith(op) for op in ["INSERT", "UPDATE", "DELETE"]
            )

            if is_dml_operation:
                # 对于 INSERT/UPDATE/DELETE，返回影响行数
                affected_rows = result.rowcount
                connection.commit()  # 提交事务

                execution_info = {
                    "sql_query": sql_query,
                    "database": driver.config.get("database", "default"),
                    "operation_type": "DML",
                    "affected_rows": affected_rows,
                }

                result_data = {
                    "message": f"操作执行成功，影响 {affected_rows} 行",
                    "execution_info": execution_info,
                    "data": [],
                }
                return result_data
            else:
                # 对于 SELECT 查询，返回查询结果
                # 获取列名
                columns = result.keys()

                # 获取数据
                rows = []
                row_count = 0
                for row in result:
                    row_data = {}
                    for i, column in enumerate(columns):
                        # 处理特殊数据类型
                        value = row[i]
                        if value is not None:
                            # 如果是 bytes 类型，转换为字符串
                            if isinstance(value, bytes):
                                value = value.decode("utf-8", errors="ignore")
                            # 如果是 datetime 类型，转换为字符串
                            elif hasattr(value, "isoformat"):
                                value = value.isoformat()
                        row_data[column] = value
                    rows.append(row_data)
                    row_count += 1

                # 获取查询执行信息
                execution_info = {
                    "sql_query": sql_query,
                    "database": driver.config.get("database", "default"),
                    "columns": list(columns),
                    "row_count": row_count,
                    "operation_type": "SELECT",
                    "limit_applied": limit
                    if sql_upper.startswith("SELECT") and "LIMIT" not in sql_upper
                    else None,
                }

                result_data = {
                    "message": "查询执行成功",
                    "execution_info": execution_info,
                    "data": rows,
                }

                return result_data

    except SQLAlchemyError as e:
        logger.error(f"数据库查询错误: {e}")
        return {
            "message": f"查询执行失败: {str(e)}",
            "error": True,
            "error_type": "SQLAlchemyError",
            "sql_query": sql_query,
        }
    except Exception as e:
        logger.error(f"查询执行未知错误: {e}")
        return {
            "message": f"查询执行失败: {str(e)}",
            "error": True,
            "error_type": "Exception",
            "sql_query": sql_query,
        }
