# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_mcp

from typing import Any, Dict, List, Union

from mcp.types import CallToolResult, Prompt, Resource

from coreason_mcp.aggregator import ToolAggregator
from coreason_mcp.config import McpConfig, McpServerConfig
from coreason_mcp.invocation_proxy import InvocationProxy
from coreason_mcp.registry import ServerRegistry
from coreason_mcp.session_manager import SessionManager
from coreason_mcp.types import ServerUrlMapping, ToolMapping
from coreason_mcp.utils.logger import logger


class McpManager:
    """
    Facade for managing MCP connections, tools, and invocations.
    """

    def __init__(self, config: Union[McpConfig, List[McpServerConfig]]) -> None:
        """
        Initialize the McpManager.

        Args:
            config: Either an McpConfig object or a list of McpServerConfig objects.
        """
        if isinstance(config, list):
            self.config = McpConfig(servers=config)
        else:
            self.config = config

        server_configs = {server.name: server for server in self.config.servers}
        self.session_manager = SessionManager(server_configs=server_configs)
        self.registry = ServerRegistry(self.session_manager, timeout=self.config.timeout)
        self.aggregator = ToolAggregator()
        self.invocation_proxy = InvocationProxy()

        self._tool_mapping: ToolMapping = {}
        self._server_urls: ServerUrlMapping = {}

        # Populate server URLs
        for server in self.config.servers:
            target = server.url if server.url else f"Command: {server.command}"
            self._server_urls[server.name] = target

    async def connect_all(self) -> None:
        """
        Connects to all configured MCP servers.
        """
        logger.info("Initializing connection to all MCP servers...")
        await self.registry.connect_all(self.config.servers)

    async def get_openai_tools(self) -> List[Dict[str, Any]]:
        """
        Aggregates tools from all connected servers and converts them to OpenAI format.

        Returns:
            A list of tool definitions.
        """
        active_sessions = self.registry.get_active_sessions()
        llm_tools, mapping = await self.aggregator.aggregate_tools(active_sessions)
        self._tool_mapping = mapping
        return llm_tools

    async def list_resources(self) -> List[Resource]:
        """
        Aggregates resources from all connected servers.

        Returns:
            A list of Resource objects.
        """
        active_sessions = self.registry.get_active_sessions()
        return await self.aggregator.aggregate_resources(active_sessions)

    async def list_prompts(self) -> List[Prompt]:
        """
        Aggregates prompts from all connected servers.

        Returns:
            A list of Prompt objects.
        """
        active_sessions = self.registry.get_active_sessions()
        return await self.aggregator.aggregate_prompts(active_sessions)

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """
        Executes a tool by name.

        Args:
            tool_name: The name of the tool to execute.
            arguments: The arguments for the tool.

        Returns:
            The result of the tool execution as a CallToolResult object.
        """
        active_sessions = self.registry.get_active_sessions()
        return await self.invocation_proxy.call_tool(
            tool_name, arguments, active_sessions, self._tool_mapping, self._server_urls
        )

    async def close(self) -> None:
        """
        Closes all active connections.
        """
        logger.info("Closing all MCP connections...")
        await self.registry.close()
        self._tool_mapping.clear()
