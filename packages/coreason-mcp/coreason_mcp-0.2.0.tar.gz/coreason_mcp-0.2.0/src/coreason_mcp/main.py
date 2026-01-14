# Copyright (c) 2025 CoReason, Inc.
#
# This software is proprietary and dual-licensed.
# Licensed under the Prosperity Public License 3.0 (the "License").
# A copy of the license is available at https://prosperitylicense.com/versions/3.0.0
# For details, see the LICENSE file.
# Commercial use beyond a 30-day trial requires a separate license.
#
# Source Code: https://github.com/CoReason-AI/coreason_mcp

import argparse
import asyncio
import json
import sys

from pydantic import ValidationError

from coreason_mcp.config import McpConfig, McpServerConfig
from coreason_mcp.manager import McpManager
from coreason_mcp.utils.logger import logger


async def run(config_path: str) -> None:
    """
    Main execution function.
    Reads config, connects to servers, and lists tools.
    """
    try:
        with open(config_path, "r") as f:
            data = json.load(f)

        # Parse config: expecting either a list of servers or a full config object
        if isinstance(data, list):
            # Assume list of server configs
            servers = [McpServerConfig(**item) for item in data]
            config = McpConfig(servers=servers)
        else:
            # Assume full config object
            try:
                if "servers" in data:
                    config = McpConfig(**data)
                else:
                    logger.error("Invalid config format. JSON must be a list or contain a 'servers' key.")
                    return
            except ValidationError as e:
                logger.error(f"Configuration Validation Error: {e}")
                return

        manager = McpManager(config)

        try:
            await manager.connect_all()
            tools = await manager.get_openai_tools()

            print(json.dumps(tools, indent=2))
            logger.info(f"Successfully retrieved {len(tools)} tools.")

        finally:
            await manager.close()

    except Exception as e:
        logger.exception(f"Failed to run coreason-mcp: {e}")
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(description="CoReason MCP Host CLI")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file")
    args = parser.parse_args()

    asyncio.run(run(args.config))


if __name__ == "__main__":  # pragma: no cover
    main()
