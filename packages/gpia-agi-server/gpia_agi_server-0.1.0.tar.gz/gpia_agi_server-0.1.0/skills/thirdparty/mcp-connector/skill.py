"""
MCP Connector Skill - External Tool Bridge
==========================================

This skill bridges external MCP (Model Context Protocol) servers
to the internal cognitive skill system.

MCP servers provide:
- GitHub: Repository management, PRs, issues
- Browser: Web automation via Playwright
- Database: PostgreSQL, Redis connections
- Search: DuckDuckGo, web fetching
- Custom: Any MCP-compliant server

The cognitive system uses this to:
1. Discover new capabilities (mcp-find)
2. Connect to external services (mcp-add)
3. Execute external tools through unified interface
4. Learn which tools work for which problems

Architecture:
```
Internal Skills ──▶ MCP Bridge ──▶ MCP Gateway ──▶ External Tools
     │                  │                              │
     ▼                  ▼                              ▼
  MemorySkill      Tool routing               GitHub, Browser,
  SafetySkill      Error handling             Postgres, etc.
  MindsetSkill     Capability discovery
```
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)

logger = logging.getLogger(__name__)


# Known MCP server categories and their tool patterns
MCP_CATALOG = {
    "github": {
        "description": "GitHub repository management",
        "tools": ["search_repositories", "create_pull_request", "list_issues", "get_file_contents"],
        "use_for": ["code review", "PR creation", "issue tracking", "repo exploration"],
    },
    "browser": {
        "description": "Web browser automation via Playwright",
        "tools": ["browser_navigate", "browser_click", "browser_snapshot", "browser_type"],
        "use_for": ["web scraping", "form filling", "UI testing", "screenshot capture"],
    },
    "postgres": {
        "description": "PostgreSQL database operations",
        "tools": ["query", "execute", "list_tables"],
        "use_for": ["data queries", "schema inspection", "data migration"],
    },
    "docker": {
        "description": "Docker container management",
        "tools": ["checkRepository", "listRepositoriesByNamespace", "createRepository"],
        "use_for": ["image management", "container registry", "deployment"],
    },
    "search": {
        "description": "Web search and content fetching",
        "tools": ["search", "fetch_content"],
        "use_for": ["research", "fact checking", "content gathering"],
    },
}


class MCPConnectorSkill(Skill):
    """
    Bridge between internal cognitive skills and external MCP tools.

    This is how the AI extends its senses and reach:
    - MCP servers are "peripheral devices"
    - Tools are "sensory inputs" and "motor outputs"
    - The bridge translates between cognitive and protocol layers

    Key capabilities:
    - discover: Find available MCP servers and tools
    - connect: Establish connection to an MCP server
    - execute: Run an MCP tool and return results
    - recommend: Suggest which MCP tool for a given task
    """

    def __init__(self):
        self._memory = None
        self._mindset = None
        self._connected_servers: Dict[str, Any] = {}

    @property
    def memory(self):
        """Lazy load MemorySkill for learning."""
        if self._memory is None:
            try:
                from skills.conscience.memory.skill import MemorySkill
                self._memory = MemorySkill()
            except Exception as e:
                logger.warning(f"MemorySkill not available: {e}")
        return self._memory

    @property
    def mindset(self):
        """Lazy load MindsetSkill for reasoning about tools."""
        if self._mindset is None:
            try:
                from skills.conscience.mindset.skill import MindsetSkill
                self._mindset = MindsetSkill()
            except Exception as e:
                logger.warning(f"MindsetSkill not available: {e}")
        return self._mindset

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="thirdparty/mcp-connector",
            name="MCP Connector",
            description="Bridge to external MCP tools (GitHub, Browser, Postgres, etc.)",
            category=SkillCategory.INTEGRATION,
            level=SkillLevel.ADVANCED,
            tags=["mcp", "integration", "external", "tools", "bridge"],
            dependencies=[
                {"skill_id": "conscience/memory", "required": False},
                {"skill_id": "conscience/mindset", "required": False},
            ],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {
                    "type": "string",
                    "enum": ["discover", "connect", "execute", "recommend", "list_connected"],
                },
                "server": {"type": "string", "description": "MCP server name"},
                "tool": {"type": "string", "description": "Tool name to execute"},
                "arguments": {"type": "object", "description": "Tool arguments"},
                "task": {"type": "string", "description": "Task description for recommendations"},
            },
            "required": ["capability"],
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "servers": {"type": "array"},
                "tools": {"type": "array"},
                "result": {"type": "object"},
                "recommendation": {"type": "object"},
            },
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")

        handlers = {
            "discover": self._discover,
            "connect": self._connect,
            "execute": self._execute_tool,
            "recommend": self._recommend,
            "list_connected": self._list_connected,
        }

        handler = handlers.get(capability)
        if not handler:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown capability: {capability}",
                skill_id=self.metadata().id,
            )

        try:
            return handler(input_data, context)
        except Exception as e:
            logger.error(f"MCP {capability} failed: {e}")
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                skill_id=self.metadata().id,
            )

    def _discover(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Discover available MCP servers and their capabilities."""
        query = input_data.get("task", "")

        # Return catalog of known servers
        servers = []
        for name, info in MCP_CATALOG.items():
            relevance = 0.5
            # Boost relevance if query matches use cases
            if query:
                for use_case in info["use_for"]:
                    if any(word in query.lower() for word in use_case.split()):
                        relevance = min(1.0, relevance + 0.2)

            servers.append({
                "name": name,
                "description": info["description"],
                "tools": info["tools"],
                "use_for": info["use_for"],
                "relevance": relevance,
            })

        # Sort by relevance
        servers.sort(key=lambda x: x["relevance"], reverse=True)

        return SkillResult(
            success=True,
            output={
                "servers": servers,
                "total": len(servers),
                "query": query,
            },
            skill_id=self.metadata().id,
        )

    def _connect(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Connect to an MCP server (register for use)."""
        server = input_data.get("server")
        if not server:
            return SkillResult(
                success=False,
                output=None,
                error="No server specified",
                skill_id=self.metadata().id,
            )

        # Check if known server
        if server not in MCP_CATALOG:
            return SkillResult(
                success=False,
                output=None,
                error=f"Unknown server: {server}. Use 'discover' to see available servers.",
                skill_id=self.metadata().id,
            )

        # Mark as connected (in a real implementation, this would call mcp-add)
        self._connected_servers[server] = {
            "status": "connected",
            "info": MCP_CATALOG[server],
        }

        # Remember this connection
        if self.memory:
            self.memory.execute({
                "capability": "experience",
                "content": f"Connected to MCP server: {server} - {MCP_CATALOG[server]['description']}",
                "memory_type": "procedural",
                "importance": 0.7,
                "context": {"skill": "mcp-connector", "server": server},
            }, context)

        return SkillResult(
            success=True,
            output={
                "server": server,
                "status": "connected",
                "tools": MCP_CATALOG[server]["tools"],
            },
            skill_id=self.metadata().id,
        )

    def _execute_tool(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Execute an MCP tool.

        Note: In a real implementation, this would call mcp__MCP_DOCKER__mcp-exec
        or the specific tool directly. This is a planning/routing layer.
        """
        server = input_data.get("server")
        tool = input_data.get("tool")
        arguments = input_data.get("arguments", {})

        if not server or not tool:
            return SkillResult(
                success=False,
                output=None,
                error="Server and tool required",
                skill_id=self.metadata().id,
            )

        # Generate the MCP tool call specification
        mcp_call = {
            "mcp_tool": f"mcp__MCP_DOCKER__{tool}",
            "server": server,
            "arguments": arguments,
            "instruction": f"Execute {tool} on {server} with args: {json.dumps(arguments)}",
        }

        return SkillResult(
            success=True,
            output={
                "call_spec": mcp_call,
                "note": "Use this specification to invoke the MCP tool directly",
            },
            skill_id=self.metadata().id,
        )

    def _recommend(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """Recommend which MCP tool to use for a task.

        Uses MindsetSkill to reason about the best tool choice.
        """
        task = input_data.get("task", "")
        if not task:
            return SkillResult(
                success=False,
                output=None,
                error="No task specified",
                skill_id=self.metadata().id,
            )

        # Find matching tools
        matches = []
        for server, info in MCP_CATALOG.items():
            for use_case in info["use_for"]:
                if any(word in task.lower() for word in use_case.split()):
                    for tool in info["tools"]:
                        matches.append({
                            "server": server,
                            "tool": tool,
                            "use_case": use_case,
                            "description": info["description"],
                        })

        if not matches:
            # Use mindset to reason about alternatives
            if self.mindset:
                result = self.mindset.execute({
                    "capability": "analyze",
                    "problem": f"What external tool or service would help with: {task}",
                    "pattern": "rapid_iteration",
                }, context)

                suggestion = result.output.get("conclusion", "") if result.success else ""
                return SkillResult(
                    success=True,
                    output={
                        "recommendation": None,
                        "alternatives": [],
                        "ai_suggestion": suggestion,
                        "note": "No exact match found. Consider the AI suggestion above.",
                    },
                    skill_id=self.metadata().id,
                )

            return SkillResult(
                success=True,
                output={
                    "recommendation": None,
                    "alternatives": list(MCP_CATALOG.keys()),
                    "note": "No matching tool found. Available servers listed in alternatives.",
                },
                skill_id=self.metadata().id,
            )

        # Return best match
        return SkillResult(
            success=True,
            output={
                "recommendation": matches[0],
                "alternatives": matches[1:5] if len(matches) > 1 else [],
                "task": task,
            },
            skill_id=self.metadata().id,
        )

    def _list_connected(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        """List currently connected MCP servers."""
        return SkillResult(
            success=True,
            output={
                "connected": list(self._connected_servers.keys()),
                "details": self._connected_servers,
            },
            skill_id=self.metadata().id,
        )


class MCPToolAdapter:
    """
    Adapter that wraps MCP tools as internal skills.

    This allows the cognitive system to treat external MCP tools
    the same way it treats internal skills - with memory, safety,
    and reasoning layers.
    """

    def __init__(self, server: str, tool_name: str, tool_schema: Dict[str, Any]):
        self.server = server
        self.tool_name = tool_name
        self.tool_schema = tool_schema

    def to_skill_metadata(self) -> SkillMetadata:
        """Convert MCP tool to SkillMetadata."""
        return SkillMetadata(
            id=f"mcp/{self.server}/{self.tool_name}",
            name=f"MCP: {self.tool_name}",
            description=self.tool_schema.get("description", f"MCP tool: {self.tool_name}"),
            category=SkillCategory.INTEGRATION,
            level=SkillLevel.INTERMEDIATE,
            tags=["mcp", "external", self.server],
        )


__all__ = ["MCPConnectorSkill", "MCPToolAdapter"]
