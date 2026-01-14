# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_mcp

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class McpServerConfig(BaseModel):
    """Configuration for a single MCP server connection."""

    name: str = Field(..., description="Unique name for the server")
    url: Optional[str] = Field(None, description="URL for SSE transport")
    command: Optional[str] = Field(None, description="Command to execute for Stdio transport")
    args: List[str] = Field(default_factory=list, description="Arguments for the command (Stdio)")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables for the command (Stdio)")
    auth_token: Optional[str] = Field(None, description="Authentication token")

    @model_validator(mode="after")
    def check_transport(self) -> "McpServerConfig":
        if not self.url and not self.command:
            raise ValueError("Either 'url' (SSE) or 'command' (Stdio) must be provided.")
        if self.url and self.command:
            raise ValueError("Cannot provide both 'url' and 'command'. Choose one transport type.")
        return self


class McpConfig(BaseModel):
    """Global configuration for the MCP Host."""

    servers: List[McpServerConfig] = Field(..., description="List of server configurations")
    timeout: float = Field(30.0, description="Default timeout for requests in seconds")
