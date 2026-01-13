"""
SQLAlchemy MCP Server 命令行入口
"""

import sys
import typer
from .server import run_stdio
from . import __version__

def version_callback(value: bool):
    if value:
        typer.echo(f"sqlalchemy-mcp-server version {__version__}")
        raise typer.Exit()

app = typer.Typer(
    name="sqlalchemy-mcp-server",
    help=f"SQLAlchemy MCP Server (v{__version__}) - 数据库操作 MCP 服务器",
    add_completion=False
)

@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit"
    )
):
    """SQLAlchemy MCP Server - 数据库操作 MCP 服务器"""
    pass

@app.command()
def stdio():
    """启动 SQLAlchemy MCP 服务器在 stdio 模式"""
    # 所有输出必须使用 stderr，避免污染 stdio 协议通信
    print("🚀 SQLAlchemy MCP Server", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print(f"版本: v{__version__}", file=sys.stderr)
    print("服务名: sqlalchemy-mcp-server", file=sys.stderr)
    print("", file=sys.stderr)
    print("🔗 启动 MCP 服务器 (stdio 模式)...", file=sys.stderr)
    print("按 Ctrl+C 退出", file=sys.stderr)

    try:
        run_stdio()
    except KeyboardInterrupt:
        print("\n服务器已停止", file=sys.stderr)
    except Exception as e:
        print(f"\n错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
    finally:
        print("服务已停止", file=sys.stderr)

if __name__ == "__main__":
    app()