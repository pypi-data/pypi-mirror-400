### 项目说明
- 模型上下文协议（MCP）服务器，允许您操作 MySQL 和 SQLite 数据库
- 项目名称：sqlalchemy_fastmcp
- 当前版本：v1.2.6
- 阅读当前目录下的 .env 文件，或者通过环境变量配置：
  - DB_TYPE: 数据库类型（支持 mysql、sqlite）
  - **MySQL 配置：**
    - DB_HOST: 数据库地址
    - DB_PORT: 数据库端口
    - DB_USER: 数据库用户名
    - DB_PASS: 数据库密码
    - DB_NAME: 数据库名称 (可选)
    - DB_CHARSET: 数据库编码 (可选)
  - **SQLite 配置：**
    - DB_NAME: 数据库文件路径（例如：/path/to/database.db 或 database.db）
- author： ferock
- email: ferock@gmail.com


### 技术参数
- python 3.11
- 框架使用 fastmcp 2.10.6
- 虚拟目录: .venv

### 目录说明
- test/ 测试目录 python 用 unittest 写单元测试，文件格式 test_<测试功能>.py
  - 测试用 docx 文件：test/office_files/模版/QN-QR-24-01-003 进料检验单（结构件）.docx
- src/ 源代码目录
  - 下面的文件是一个功能对应一个 py 文件
- pyproject.toml 项目配置文件
- VERSION 版本号文件
- build_and_publish_uv.sh 打包命令
- .env 测试用的环境变量

### 配置说明

#### 方法一：.env 文件配置

**MySQL 配置示例：**
```bash
DB_TYPE=mysql
DB_HOST=192.168.1.73
DB_PORT=3306
DB_USER=your_username
DB_PASS=your_password
DB_NAME=your_database
DB_CHARSET=utf8mb4
```

**SQLite 配置示例：**
```bash
DB_TYPE=sqlite
DB_NAME=/path/to/database.db
```
或使用相对路径：
```bash
DB_TYPE=sqlite
DB_NAME=database.db
```

#### 方法二：环境变量配置

**MySQL 环境变量：**
```bash
export DB_TYPE=mysql
export DB_HOST=1.1.1.1
export DB_PORT=3306
export DB_USER=your_username
export DB_PASS=your_password
export DB_NAME=your_database
export DB_CHARSET=utf8mb4
```

**SQLite 环境变量：**
```bash
export DB_TYPE=sqlite
export DB_NAME=/path/to/database.db
```

#### 方法三：MCP 配置中的环境变量

**MySQL 配置示例：**
```json
{
  "mcpServers": {
    "sqlalchemy-mcp": {
      "command": "uvx",
      "args": [
        "--from", "sqlalchemy_fastmcp==1.2.6", "sqlalchemy-mcp-server", "stdio"],
      "env": {
        "DB_TYPE": "mysql",
        "DB_HOST": "1.1.1.1",
        "DB_PORT": "3306",
        "DB_USER": "your_username",
        "DB_PASS": "your_password",
        "DB_NAME": "your_database",
        "DB_CHARSET": "utf8mb4"
      }
    }
  }
}
```

**SQLite 配置示例：**
```json
{
  "mcpServers": {
    "sqlalchemy-mcp-sqlite": {
      "command": "uvx",
      "args": [
        "--from", "sqlalchemy_fastmcp==1.2.6", "sqlalchemy-mcp-server", "stdio"],
      "env": {
        "DB_TYPE": "sqlite",
        "DB_NAME": "/path/to/database.db"
      }
    }
  }
}
```

### 权限控制

为了防止误操作，系统默认禁用所有数据修改操作。您可以通过环境变量来控制权限：

- `ALLOW_INSERT_OPERATION`: 控制INSERT操作权限（默认: false）
  - 影响操作：`INSERT INTO`, `REPLACE INTO`, `LOAD DATA`
- `ALLOW_UPDATE_OPERATION`: 控制UPDATE/ALTER操作权限（默认: false）
  - 影响操作：`UPDATE SET`, `ALTER TABLE/DATABASE`, `CREATE TABLE/DATABASE/INDEX`, `TRUNCATE TABLE`
- `ALLOW_DELETE_OPERATION`: 控制DELETE/DROP操作权限（默认: false）
  - 影响操作：`DELETE FROM`, `DROP TABLE/DATABASE/VIEW/PROCEDURE/FUNCTION`

**注意**: SELECT等查询操作始终被允许，不受权限控制影响。

### 功能
- [x] show_databases - 显示数据库列表
- [x] get_database_info - 获取数据库配置信息
- [x] test_database_connection - 测试数据库连接
- show_tables  - 显示当前数据库内数据表的列表
- exec_query - 执行 SQL 查询

### 发布

```bash
bash ./build_and_publish_uv.sh
```

### 使用

使用 `uvx` 命令可以直接运行，无需预先安装，uvx 会自动处理依赖和安装：

#### 方法一：指定版本号（推荐）
```bash
uvx --from sqlalchemy_fastmcp==1.2.6 sqlalchemy-mcp-server stdio
```

#### 方法二：使用最新版本
```bash
uvx --from sqlalchemy_fastmcp sqlalchemy-mcp-server stdio
```

**注意**: 必须在命令末尾添加 `stdio` 子命令来启动 MCP 服务器。

### MCP 参考命令

以下命令可以直接在终端中运行以启动 MCP 服务器：

```bash
uvx  --from sqlalchemy_fastmcp==1.2.6 sqlalchemy-mcp-server stdio
```

此命令会：
- 从 Nexus3 仓库安装 sqlalchemy_fastmcp 包（版本 1.2.6）
- 自动处理所有依赖关系
- 启动 sqlalchemy-mcp-server 在 stdio 模式下运行
- 无需预先安装包，uvx 会自动下载和运行

### 数据库支持

#### MySQL
- 完整支持所有 MySQL 功能
- 支持查看数据库列表、表结构、执行 SQL 查询等
- 需要配置连接信息（主机、端口、用户名、密码等）

#### SQLite
- 支持本地 SQLite 数据库文件
- 使用文件路径作为数据库标识
- 无需配置用户名密码等连接信息
- 支持绝对路径和相对路径
- 注意：SQLite 是单文件数据库，`show_databases` 功能会返回当前数据库文件信息

### SSH 隧道连接 (v1.2.6+)
- set_database_source_on_ssh_tool - 通过 SSH 隧道安全连接远程数据库
- stop_ssh_tunnel_tool - 关闭 SSH 隧道
- get_ssh_tunnel_status_tool - 获取隧道状态
支持密码和密钥两种认证方式（同时提供时优先密钥），适合长运行 MCP 服务。