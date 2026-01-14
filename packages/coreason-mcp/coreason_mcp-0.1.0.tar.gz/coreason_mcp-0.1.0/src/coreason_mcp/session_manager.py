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
from typing import AsyncGenerator

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

from coreason_mcp.config import McpServerConfig


class SessionManager:
    """
    Manages connections to MCP servers.
    Handles initialization and session lifecycle for both SSE and Stdio transports.
    """

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

    def _get_headers(self, config: McpServerConfig) -> dict[str, str]:
        """Constructs headers for SSE connections."""
        headers = {}
        if config.auth_token:
            headers["Authorization"] = f"Bearer {config.auth_token}"
        return headers
