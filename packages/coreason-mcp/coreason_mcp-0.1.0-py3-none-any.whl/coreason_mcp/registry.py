# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_mcp

import asyncio
from contextlib import AsyncExitStack
from typing import Dict, List

from mcp import ClientSession

from coreason_mcp.config import McpServerConfig
from coreason_mcp.session_manager import SessionManager
from coreason_mcp.utils.logger import logger


class ServerRegistry:
    """
    Manages a registry of active MCP server connections.
    Handles connection lifecycle, retries, and health checks.
    """

    def __init__(
        self,
        session_manager: SessionManager,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize the ServerRegistry.

        Args:
            session_manager: The SessionManager instance to use for creating connections.
            max_retries: Maximum number of connection attempts per server.
            retry_delay: Delay in seconds between retries (simple backoff multiplier could be added).
            timeout: Default timeout for requests in seconds.
        """
        self.session_manager = session_manager
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self._exit_stack = AsyncExitStack()
        self._active_sessions: Dict[str, ClientSession] = {}
        self._lock = asyncio.Lock()

    async def connect_all(self, server_configs: List[McpServerConfig]) -> None:
        """
        Connects to all provided server configurations with retry logic.

        Args:
            server_configs: List of server configurations to connect to.
        """
        logger.info("ServerRegistry: Initializing connections...")
        # We must connect sequentially to ensure the context manager is entered
        # in the same task that will eventually close it (the main task).
        # Using asyncio.TaskGroup here would cause 'anyio' RuntimeErrors during shutdown.
        for config in server_configs:
            await self._connect_with_retry(config)

    async def _connect_with_retry(self, config: McpServerConfig) -> None:
        """
        Attempts to connect to a single server with retries.

        Args:
            config: The server configuration.
        """
        attempt = 0
        while attempt <= self.max_retries:
            try:
                attempt += 1
                target = config.url if config.url else f"Command: {config.command}"
                logger.info(
                    f"Connecting to MCP Server: {config.name} at {target} (Attempt {attempt}/{self.max_retries + 1})"
                )

                # Enter context manager and get session
                # Lock is required because AsyncExitStack.enter_async_context is not thread/task safe
                # when modifying the internal stack structure concurrently.
                async with self._lock:
                    session = await self._exit_stack.enter_async_context(
                        self.session_manager.connect(config, timeout=self.timeout)
                    )

                # Perform Health Check
                logger.debug(f"Pinging {config.name}...")
                await session.send_ping()

                self._active_sessions[config.name] = session
                logger.info(f"Connected to {config.name}")
                return  # Success

            except Exception as e:
                logger.warning(f"Failed to connect to {config.name} (Attempt {attempt}): {e}")
                if attempt <= self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"Max retries reached for {config.name}. Skipping.")

    def get_active_sessions(self) -> Dict[str, ClientSession]:
        """
        Returns a dictionary of active sessions.

        Returns:
            Dict mapping server names to ClientSession objects.
        """
        return self._active_sessions

    async def close(self) -> None:
        """
        Closes all active connections and cleans up resources.
        """
        logger.info("ServerRegistry: Closing all connections...")
        async with self._lock:
            await self._exit_stack.aclose()
        self._active_sessions.clear()
