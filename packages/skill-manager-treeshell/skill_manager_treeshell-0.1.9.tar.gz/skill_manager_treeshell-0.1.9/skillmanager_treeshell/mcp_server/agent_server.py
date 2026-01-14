#!/usr/bin/env python3
"""
CustomTreeshell Agent MCP Server - Tree-based navigation REPL for AI agents
"""
import json
import os
from enum import Enum
from typing import Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from mcp.shared.exceptions import McpError

from skillmanager_treeshell import SkillManagerTreeShell


class TreeShellTools(str, Enum):
    RUN_CONVERSATION_SHELL = "run_conversation_shell"


class SkillManagerTreeshellAgentMCPServer:
    """MCP Server for Skill Manager TreeShell"""

    def __init__(self):
        self.shell = None

    def _find_user_config(self, heaven_data_dir: str, library_prefix: str) -> str:
        """Find user config directory for this library in HEAVEN_DATA_DIR."""
        try:
            if not os.path.exists(heaven_data_dir):
                return None
            for item in os.listdir(heaven_data_dir):
                if item.startswith(library_prefix):
                    item_path = os.path.join(heaven_data_dir, item)
                    if os.path.isdir(item_path):
                        configs_path = os.path.join(item_path, 'configs')
                        if os.path.exists(configs_path):
                            return configs_path
            return None
        except Exception:
            return None

    async def run_conversation_shell(self, command: str) -> dict:
        if not self.shell:
            try:
                heaven_data = os.getenv("HEAVEN_DATA_DIR", "/tmp/heaven_data")
                os.environ["HEAVEN_DATA_DIR"] = heaven_data
                os.makedirs(heaven_data, exist_ok=True)
                user_config_path = self._find_user_config(heaven_data, "skillmanager_treeshell")
                self.shell = SkillManagerTreeShell(user_config_path=user_config_path)
            except Exception as e:
                return {"success": False, "error": f"Shell failed to initialize: {e}"}
        
        try:
            response = self.shell.handle_command(command)
            return {"success": True, "response": response}
        except Exception as e:
            return {"success": False, "error": str(e)}


async def serve() -> None:
    server = Server("skillmanager_treeshell-agent-shell")
    shell_server = SkillManagerTreeshellAgentMCPServer()
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=TreeShellTools.RUN_CONVERSATION_SHELL.value,
                description="""Skill Manager - Three-tier skill architecture: global catalog, equipped state, skillsets.

Actions (coordinate | name):

=== Global Catalog ===
0.1.1 | list_skills - List all skills in global catalog.
0.1.2 | list_domains - List all available skill domains.
0.1.3 | list_by_domain - List all skills and skillsets in a domain.
  Args: domain (str)
0.1.4 | get_skill - Get full content of a skill.
  Args: name (str)
0.1.5 | create_skill - Create a skill in global catalog.
  Args: name (str), domain (str), content (str), description (str), subdomain (str, optional)
0.1.6 | search_skills - Search skills and skillsets using RAG.
  Args: query (str), n_results (int, optional)

=== Equipped State ===
0.1.7 | list_equipped - List currently equipped skills.
0.1.8 | get_equipped_content - Get full content of all equipped skills.
0.1.9 | equip - Equip a skill or skillset. Loads it into working memory.
  Args: name (str)
0.1.10 | unequip - Unequip a skill.
  Args: name (str)
0.1.11 | unequip_all - Clear all equipped skills.

=== Skillsets ===
0.1.12 | list_skillsets - List all skillsets.
0.1.13 | create_skillset - Create a skillset with domain.
  Args: name (str), domain (str), description (str), skills (str, comma-separated), subdomain (str, optional)
0.1.14 | add_to_skillset - Add a skill to a skillset.
  Args: skillset_name (str), skill_name (str)
0.1.15 | match_skilllog - Match a SkillLog prediction against catalog.
  Args: prediction (str)

=== Personas ===
0.1.16 | list_personas - List all personas.
0.1.17 | create_persona - Create a persona bundling frame, MCP set, skillset, and identity.
  Args: name (str), domain (str), description (str), frame (str), mcp_set (str, optional), skillset (str, optional), carton_identity (str, optional), subdomain (str, optional)
0.1.18 | equip_persona - Equip a persona - loads frame, attempts skillset, reports MCP set needs.
  Args: name (str)
0.1.19 | get_active_persona - Get the currently active persona.
0.1.20 | deactivate_persona - Deactivate current persona and unequip all skills.

Commands:
- 'nav' - Show tree structure
- 'jump <coordinate>' - Navigate to node (e.g., 'jump list_skills')
- '<coordinate>.exec {"args": "values"}' - Jump and execute (e.g., 'equip.exec {"name": "my-skill"}')
- 'exec {"args"}' - Execute current node""",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "TreeShell command to execute"
                        }
                    },
                    "required": ["command"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
        if name == TreeShellTools.RUN_CONVERSATION_SHELL.value:
            result = await shell_server.run_conversation_shell(arguments.get("command", ""))
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        raise McpError(f"Unknown tool: {name}")
    
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options)


if __name__ == "__main__":
    import asyncio
    asyncio.run(serve())
