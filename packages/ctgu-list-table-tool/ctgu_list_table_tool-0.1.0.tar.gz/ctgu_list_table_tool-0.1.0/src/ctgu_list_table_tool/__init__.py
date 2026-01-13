"""
FastMCP quickstart example.

Run from the repository root:
    uv run examples/snippets/servers/fastmcp_quickstart.py
"""
from langchain_core.tools import BaseTool
from mcp.server.fastmcp import FastMCP
from db_utils import MySQLDatabaseManager
from log_util import log
from postgre_utils import PostgreDatabaseManager

class PostgresqlListTablesTool(BaseTool):
    """列出数据库中的所有表及其描述信息"""
    name: str = "sql_db_list_tables"
    description: str = "列出MySQL数据库中的所有表名及其描述信息。"

    # 数据库管理器实例
    db_manager: PostgreDatabaseManager

    def _run(self) -> str:
        """列出数据库中的所有表及其描述信息"""
        try:
            tables_info = self.db_manager.get_tables_with_comments()
            result = f"数据库中共有 {len(tables_info)} 个表:\n\n"
            for i, table_info in enumerate(tables_info):
                table_name = table_info['table_name']
                table_comment = table_info['table_comment']

                # 处理空描述的情况
                if not table_comment or table_comment.isspace():
                    description_display = "(暂无描述)"
                else:
                    description_display = table_comment

                result += f"{i + 1}. 表名: {table_name}\n"
                result += f"   描述: {description_display}\n\n"
            return result
        except Exception as e:
            log.exception(e)
            return f"列出表信息时出错: {str(e)}"

    async def _arun(self) -> str:
        """异步执行"""
        return self._run()

class MysqlListTablesTool(BaseTool):
    """列出数据库中的所有表及其描述信息"""
    name: str = "sql_db_list_tables"
    description: str = "列出MySQL数据库中的所有表名及其描述信息。"

    # 数据库管理器实例
    db_manager: MySQLDatabaseManager

    def _run(self) -> str:
        """列出数据库中的所有表及其描述信息"""
        try:
            tables_info = self.db_manager.get_tables_with_comments()
            result = f"数据库中共有 {len(tables_info)} 个表:\n\n"
            for i, table_info in enumerate(tables_info):
                table_name = table_info['table_name']
                table_comment = table_info['table_comment']

                # 处理空描述的情况
                if not table_comment or table_comment.isspace():
                    description_display = "(暂无描述)"
                else:
                    description_display = table_comment

                result += f"{i + 1}. 表名: {table_name}\n"
                result += f"   描述: {description_display}\n\n"
            return result
        except Exception as e:
            log.exception(e)
            return f"列出表信息时出错: {str(e)}"

    async def _arun(self) -> str:
        """异步执行"""
        return self._run()

# Create an MCP server
mcp = FastMCP("ListTablesTool", json_response=True)

# Add an addition tool
@mcp.tool()
def list_tables_tool(connection_config: str) -> str:
    """根据数据库类型和数据库连接配置,列出数据库中的所有表及其描述信息"""
    # connection_string = f"postgresql+psycopg2://wcpadmin:ctgu2025@172.16.12.43:30235/postgres?client_encoding=utf8"
    # connection_string = f"mysql+pymysql://root:123456@localhost:3306/foodmart2"
    if connection_config.lower().startswith("postgresql"):
        db_manager = PostgreDatabaseManager(connection_config)
        tool = PostgresqlListTablesTool(db_manager=db_manager)
    else:
        db_manager = MySQLDatabaseManager(connection_config)
        tool = MysqlListTablesTool(db_manager=db_manager)

    return tool.invoke({})

# Run with streamable HTTP transport
def main() -> None:
    mcp.run(transport='stdio')
