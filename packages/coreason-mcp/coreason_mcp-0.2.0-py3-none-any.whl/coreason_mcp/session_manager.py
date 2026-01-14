# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_mcp

from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Any, AsyncGenerator, Dict, Optional

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

from coreason_mcp.config import McpServerConfig


class SessionManager:
    """
    Manages connections to MCP servers.
    Handles initialization and session lifecycle for both SSE and Stdio transports.
    """

    def __init__(self, server_configs: Optional[Dict[str, McpServerConfig]] = None) -> None:
        """
        Initialize the SessionManager.

        Args:
            server_configs: Optional mapping of agent_id/server_name to McpServerConfig.
        """
        self.server_configs = server_configs or {}

    @asynccontextmanager
    async def connect(self, config: McpServerConfig, timeout: float = 30.0) -> AsyncGenerator[ClientSession, None]:
        """
        Establishes a connection to an MCP server based on the configuration.

        Args:
            config: The configuration for the MCP server connection.
            timeout: Default timeout for requests in seconds.

        Yields:
            An active, initialized ClientSession.
        """
        read_timeout = timedelta(seconds=timeout)

        if config.url:
            # SSE Transport
            # We pass timeout to sse_client for the connection/handshake
            async with sse_client(url=config.url, headers=self._get_headers(config), timeout=timeout) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=read_timeout) as session:
                    await session.initialize()
                    yield session

        elif config.command:
            # Stdio Transport
            params = StdioServerParameters(
                command=config.command,
                args=config.args,
                env=config.env if config.env else None,
            )
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write, read_timeout_seconds=read_timeout) as session:
                    await session.initialize()
                    yield session
        else:
            raise ValueError(f"Invalid configuration for server '{config.name}': Missing URL or Command.")

    async def execute_agent(self, agent_id: str, input_data: Dict[str, Any], context: Any) -> Any:
        """
        Orchestrates the execution of an agent by connecting to the MCP server/agent and running it.

        Args:
            agent_id: The ID of the agent (maps to server name).
            input_data: The arguments to pass to the agent/tool.
            context: Execution context (unused currently).

        Returns:
            The result of the agent execution.

        Raises:
            ValueError: If the agent_id is not found or execution is ambiguous.
        """
        if agent_id not in self.server_configs:
            raise ValueError(f"No configuration found for agent '{agent_id}'.")

        config = self.server_configs[agent_id]

        async with self.connect(config) as session:
            # List tools to find the correct entry point
            result = await session.list_tools()
            tools = result.tools

            target_tool_name = None

            if len(tools) == 1:
                # If only one tool exists, assume it is the agent's entry point
                target_tool_name = tools[0].name
            else:
                # If multiple tools, look for one that matches the agent_id
                for tool in tools:
                    if tool.name == agent_id:
                        target_tool_name = tool.name
                        break

            if not target_tool_name:
                raise ValueError(
                    f"Ambiguous agent execution for '{agent_id}': "
                    f"Found {len(tools)} tools and none matched the agent ID."
                )

            # Call the tool
            return await session.call_tool(target_tool_name, input_data)

    def _get_headers(self, config: McpServerConfig) -> dict[str, str]:
        """Constructs headers for SSE connections."""
        headers = {}
        if config.auth_token:
            headers["Authorization"] = f"Bearer {config.auth_token}"
        return headers
