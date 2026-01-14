#!/usr/bin/env python3
"""
Gnosys User MCP Server - Tree-based navigation REPL for humans
"""
import json
import logging
import os
import traceback
from enum import Enum
from typing import Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.shared.exceptions import McpError

from gnosys_treeshell import GnosysTreeShell
from heaven_tree_repl import render_response

logger = logging.getLogger(__name__)


class TreeShellTools(str, Enum):
    RUN_CONVERSATION_SHELL = "run_conversation_shell"


class GnosysMCPServer:
    """MCP Server for Gnosys TreeShell"""

    def __init__(self):
        self.shell = None

    async def run_conversation_shell(self, command: str) -> dict:
        if not self.shell:
            try:
                if not os.getenv("HEAVEN_DATA_DIR"):
                    os.environ["HEAVEN_DATA_DIR"] = "/tmp/heaven_data"
                    os.makedirs("/tmp/heaven_data", exist_ok=True)
                self.shell = GnosysTreeShell()
            except Exception as e:
                logger.error(f"Shell initialization failed: {traceback.format_exc()}")
                return {
                    "success": False,
                    "error": f"Shell failed to initialize: {e}"
                }

        try:
            result = await self.shell.handle_command(command)
            rendered_output = render_response(result)

            return {
                "success": True,
                "command": command,
                "rendered_output": rendered_output,
                "raw_result": result
            }
        except Exception as e:
            logger.error(f"Command execution failed: {traceback.format_exc()}")
            return {
                "success": False,
                "error": f"Error executing command '{command}': {str(e)}"
            }


async def serve() -> None:
    server = Server("gnosys-treeshell")
    shell_server = GnosysMCPServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=TreeShellTools.RUN_CONVERSATION_SHELL.value,
                description="""GNOSYS MCP Router - Manage and execute MCP server actions via TreeShell navigation.

Actions (coordinate | name):

0.0.1 | discover_server_actions - **PREFERRED STARTING POINT**: Discover available actions from servers.
  Args: user_query (str), server_names (List[str], optional)

0.0.2 | execute_action - Execute a specific action with provided parameters.
  Args: server_name (str), action_name (str), path_params (JSON), query_params (JSON), body_schema (JSON)

0.0.3 | get_action_details - Get detailed information about a specific action.
  Args: server_name (str), action_name (str)

0.0.4 | handle_auth_failure - Handle authentication failures.
  Args: server_name (str), intention ('get_auth_url'|'save_auth_data'), auth_data (dict, optional)

0.0.5 | manage_servers - Manage MCP server connections and Sets.
  Args: list_configured_mcps, list_sets, connect, connect_set, disconnect, disconnect_all, etc.

0.0.6 | search_documentation - Search server action docs by keyword.
  Args: query (str), server_name (str), max_results (int)

0.0.7 | search_mcp_catalog - Search offline catalog for tools/Sets.
  Args: query (str), max_results (int)

Commands:
- 'nav' - Show tree structure
- 'jump <coordinate>' - Navigate to node (e.g., 'jump discover_server_actions')
- '<coordinate>.exec {"args": "values"}' - Jump and execute (e.g., 'discover_server_actions.exec {"user_query": "..."}')
- 'exec {"args"}' - Execute current node""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "TreeShell command: 'nav' to see tree, 'jump <id>' to navigate, '<id>.exec {\"arg\": \"value\"}' to execute"
                        }
                    },
                    "required": ["command"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
        try:
            match name:
                case TreeShellTools.RUN_CONVERSATION_SHELL.value:
                    command = arguments.get("command", "")
                    result = await shell_server.run_conversation_shell(command)

                    if result.get("success"):
                        output_text = result.get("rendered_output", "No output available")
                    else:
                        output_text = f"❌ Error: {result.get('error', 'Unknown error')}"

                case _:
                    raise ValueError(f"Unknown tool: {name}")

            return [
                TextContent(type="text", text=output_text)
            ]

        except Exception as e:
            logger.error(f"Tool call failed: {traceback.format_exc()}")
            raise ValueError(f"Error processing TreeShell operation: {str(e)}")

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)


if __name__ == "__main__":
    import asyncio
    asyncio.run(serve())
