# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_mcp

"""
Standardizes external data access using the Model Context Protocol.
"""

__version__ = "0.2.0"
__author__ = "Gowtham A Rao"
__email__ = "gowtham.rao@coreason.ai"

from .config import McpConfig, McpServerConfig
from .manager import McpManager

__all__ = ["McpManager", "McpServerConfig", "McpConfig"]
