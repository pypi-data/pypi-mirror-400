# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_mcp

from typing import Any, Dict

import httpx
import jsonschema
from mcp import ClientSession
from mcp.types import AudioContent, CallToolResult, EmbeddedResource, ImageContent, ResourceLink, TextContent

from coreason_mcp.types import ServerUrlMapping, ToolMapping
from coreason_mcp.utils.logger import logger


class InvocationError(Exception):
    """Raised when the server returns an error during tool execution."""

    pass


class ToolNotFoundError(Exception):
    """Raised when the requested tool is not found."""

    pass


class ServerConnectionError(Exception):
    """Raised when the target server session is not available."""

    pass


class InvocationProxy:
    """
    Routes tool execution requests to the appropriate MCP session and handles
    result processing and error translation.
    """

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        sessions: Dict[str, ClientSession],
        tool_mapping: ToolMapping,
        server_urls: ServerUrlMapping,
    ) -> CallToolResult:
        """
        Executes a tool on the appropriate MCP server.

        Args:
            tool_name: The name of the tool to execute (namespaced name).
            arguments: The arguments to pass to the tool.
            sessions: A dictionary of active ClientSessions.
            tool_mapping: A mapping resolving namespaced tool names to server and original names.
            server_urls: A mapping of server names to their URLs (or command strings).

        Returns:
            The result of the tool execution as a CallToolResult object.

        Raises:
            ToolNotFoundError: If the tool name is not in the mapping.
            ServerConnectionError: If the server session is not found.
            InvocationError: If the tool execution fails or returns an error.
        """
        if tool_name not in tool_mapping:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found.")

        mapping_info = tool_mapping[tool_name]
        server_name = str(mapping_info["server"])
        original_name = str(mapping_info["original_name"])
        input_schema = mapping_info.get("inputSchema")
        is_sensitive = mapping_info.get("sensitive", False)

        # Validate arguments against schema
        if input_schema:
            try:
                jsonschema.validate(instance=arguments, schema=input_schema)
            except jsonschema.ValidationError as e:
                if is_sensitive:
                    logger.error(f"Validation failed for tool '{tool_name}' [SENSITIVE]: Arguments hidden.")
                else:
                    logger.error(f"Validation failed for tool '{tool_name}': {e}")

                # We raise the error with the message, but be careful not to include the whole 'e' object
                # which might print the instance in its string representation.
                # e.message usually contains "123 is not of type 'integer'" which leaks data.
                if is_sensitive:
                    raise InvocationError(
                        f"Validation failed for tool '{tool_name}': Arguments invalid (Sensitive)."
                    ) from None
                else:
                    raise InvocationError(f"Validation failed for tool '{tool_name}': {e.message}") from e

        if server_name not in sessions:
            raise ServerConnectionError(f"Session for server '{server_name}' is not active.")

        session = sessions[server_name]
        server_url = server_urls.get(server_name, "Unknown URL")

        # Log invocation
        if is_sensitive:
            logger.info(f"Tool Invoked: {tool_name} on {server_name} ({server_url}) [SENSITIVE]")
        else:
            logger.info(f"Tool Invoked: {tool_name} on {server_name} ({server_url})")

        try:
            result: CallToolResult = await session.call_tool(original_name, arguments)

            if result.isError:
                logger.error(f"Tool Invoked: {tool_name} - Fail (Server Error)")
                # Extract error message from content if available
                error_msg = self._extract_content(result)
                if is_sensitive:
                    raise InvocationError("Tool execution failed: [SENSITIVE ERROR HIDDEN]")
                raise InvocationError(f"Tool execution failed: {error_msg}")

            logger.info(f"Tool Invoked: {tool_name} - Success")
            return result

        except InvocationError:
            # Re-raise explicit invocation errors
            raise
        except (ConnectionError, TimeoutError, EOFError, httpx.TimeoutException, httpx.NetworkError) as e:
            # Infrastructure/Network errors
            # httpx.TimeoutException covers ReadTimeout, ConnectTimeout, etc.
            # httpx.NetworkError covers other transport errors
            logger.error(f"Tool Invoked: {tool_name} - Network Error: {e}")
            raise ServerConnectionError(f"Network error communicating with server: {e}") from e
        except Exception as e:
            # Catch protocol errors (including AttributeError if result is invalid) and re-raise as InvocationError
            if is_sensitive:
                logger.error(f"Tool Invoked: {tool_name} - Fail: [SENSITIVE ERROR HIDDEN]")
                raise InvocationError(f"Protocol error executing tool '{tool_name}': [SENSITIVE]") from None
            else:
                logger.error(f"Tool Invoked: {tool_name} - Fail: {e}")
                raise InvocationError(f"Protocol error executing tool '{tool_name}': {e}") from e

    def _extract_content(self, result: CallToolResult) -> str:
        """
        Extracts text content from the CallToolResult.

        Args:
            result: The result object from the tool call.

        Returns:
            A string representation of the result content.
        """
        output_parts = []
        for content in result.content:
            if isinstance(content, TextContent):
                output_parts.append(content.text)
            elif isinstance(content, ImageContent):
                output_parts.append(f"[Image: {content.mimeType}]")
            elif isinstance(content, AudioContent):
                output_parts.append(f"[Audio: {content.mimeType}]")
            elif isinstance(content, ResourceLink):
                output_parts.append(f"[ResourceLink: {content.uri}]")
            elif isinstance(content, EmbeddedResource):
                output_parts.append(f"[EmbeddedResource: {content.resource}]")
            # Handle other content types if necessary (e.g. EmbeddedResource)
            else:
                output_parts.append(str(content))

        return "\n".join(output_parts)
