# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_mcp

from typing import Any, Dict, TypeAlias

# Defines the mapping structure for tools:
# {
#     "namespaced_tool_name": {
#         "server": "server_name",
#         "original_name": "original_tool_name",
#         "inputSchema": {...},
#         "sensitive": bool
#     }
# }
ToolMapping: TypeAlias = Dict[str, Dict[str, Any]]

# Mapping of server names to URLs or Command strings
ServerUrlMapping: TypeAlias = Dict[str, str]
