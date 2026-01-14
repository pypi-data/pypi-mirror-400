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
from typing import Any, Dict, List, Tuple

from mcp import ClientSession
from mcp.types import Prompt, Resource, Tool

from coreason_mcp.utils.logger import logger


class ToolAggregator:
    """
    Aggregates capabilities (tools, resources, prompts) from multiple MCP sessions,
    handles naming collisions, and translates them to consuming formats.
    """

    async def aggregate_tools(
        self, sessions: Dict[str, ClientSession]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
        """
        Fetches tools from all sessions, resolves naming conflicts, and converts to OpenAI format.

        Args:
            sessions: A dictionary mapping server names to active ClientSession objects.

        Returns:
            A tuple containing:
            1. A list of tool definitions in OpenAI JSON format.
            2. A mapping of {final_tool_name: {"server": server_name, "original_name": tool_name, "inputSchema": ...}}.
        """
        all_tools: List[Tuple[str, Tool]] = []
        tool_counts: Dict[str, int] = {}

        # 1. Collect all tools concurrently
        async def fetch_tools(s_name: str, sess: ClientSession) -> List[Tuple[str, Tool]]:
            tools_list: List[Tuple[str, Tool]] = []
            cursor = None
            while True:
                result = await sess.list_tools(cursor=cursor)
                for tool in result.tools:
                    tools_list.append((s_name, tool))
                cursor = result.nextCursor
                if not cursor:
                    break
            return tools_list

        tasks = [fetch_tools(name, session) for name, session in sessions.items()]
        # Enable return_exceptions=True to allow partial success
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten results and count names
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                # Log error but do not crash
                server_name = list(sessions.keys())[i]
                logger.error(f"Failed to list tools from server '{server_name}': {res}")
                continue

            # res is List[Tuple[str, Tool]]
            for item in res:  # type: ignore
                all_tools.append(item)
                tool_name = item[1].name
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1

        llm_tools: List[Dict[str, Any]] = []
        tool_mapping: Dict[str, Dict[str, Any]] = {}

        # 2. Process tools and resolve conflicts
        used_names = set()

        for server_name, tool in all_tools:
            original_name = tool.name
            final_name = original_name

            # Initial Rename Logic: If original name is not unique globally, prefix it.
            if tool_counts[original_name] > 1:
                final_name = f"{server_name}_{original_name}"

            # Secondary Collision Check: Ensure final_name is unique in our output set.
            # E.g., if we renamed "search" -> "serverA_search", but "serverA_search" already existed.
            base_final_name = final_name
            counter = 2
            while final_name in used_names:
                final_name = f"{base_final_name}_{counter}"
                counter += 1

            used_names.add(final_name)

            # Check for sensitivity flag in tool metadata (convention: meta={"sensitive": True})
            is_sensitive = False
            # tool.meta is explicitly Optional[Dict[str, Any]] in pydantic model but let's be safe
            if tool.meta and isinstance(tool.meta, dict):
                is_sensitive = tool.meta.get("sensitive", False)

            # 3. Build Mapping
            tool_mapping[final_name] = {
                "server": server_name,
                "original_name": original_name,
                "inputSchema": tool.inputSchema,
                "sensitive": is_sensitive,
            }

            # 4. Convert to OpenAI Format
            llm_tool = {
                "type": "function",
                "function": {
                    "name": final_name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            llm_tools.append(llm_tool)

        return llm_tools, tool_mapping

    async def aggregate_resources(self, sessions: Dict[str, ClientSession]) -> List[Resource]:
        """
        Fetches resources from all sessions, resolving naming conflicts in the resource names.

        Args:
            sessions: A dictionary mapping server names to active ClientSession objects.

        Returns:
            A list of Resource objects with potentially modified names.
        """
        all_resources: List[Tuple[str, Resource]] = []
        resource_counts: Dict[str, int] = {}

        async def fetch_resources(s_name: str, sess: ClientSession) -> List[Tuple[str, Resource]]:
            res_list: List[Tuple[str, Resource]] = []
            cursor = None
            while True:
                result = await sess.list_resources(cursor=cursor)
                for resource in result.resources:
                    res_list.append((s_name, resource))
                cursor = result.nextCursor
                if not cursor:
                    break
            return res_list

        tasks = [fetch_resources(name, session) for name, session in sessions.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, res in enumerate(results):
            if isinstance(res, Exception):
                server_name = list(sessions.keys())[i]
                logger.error(f"Failed to list resources from server '{server_name}': {res}")
                continue
            for item in res:  # type: ignore
                all_resources.append(item)
                r_name = item[1].name
                resource_counts[r_name] = resource_counts.get(r_name, 0) + 1

        final_resources: List[Resource] = []
        used_names = set()

        for server_name, resource in all_resources:
            original_name = resource.name
            final_name = original_name

            if resource_counts[original_name] > 1:
                final_name = f"{server_name}_{original_name}"

            base_final_name = final_name
            counter = 2
            while final_name in used_names:
                final_name = f"{base_final_name}_{counter}"
                counter += 1

            used_names.add(final_name)

            # Create a copy with the new name
            # Note: Pydantic models are immutable-ish, so we use model_copy
            new_resource = resource.model_copy(update={"name": final_name})
            final_resources.append(new_resource)

        return final_resources

    async def aggregate_prompts(self, sessions: Dict[str, ClientSession]) -> List[Prompt]:
        """
        Fetches prompts from all sessions, resolving naming conflicts in the prompt names.

        Args:
            sessions: A dictionary mapping server names to active ClientSession objects.

        Returns:
            A list of Prompt objects with potentially modified names.
        """
        all_prompts: List[Tuple[str, Prompt]] = []
        prompt_counts: Dict[str, int] = {}

        async def fetch_prompts(s_name: str, sess: ClientSession) -> List[Tuple[str, Prompt]]:
            p_list: List[Tuple[str, Prompt]] = []
            cursor = None
            while True:
                result = await sess.list_prompts(cursor=cursor)
                for prompt in result.prompts:
                    p_list.append((s_name, prompt))
                cursor = result.nextCursor
                if not cursor:
                    break
            return p_list

        tasks = [fetch_prompts(name, session) for name, session in sessions.items()]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, res in enumerate(results):
            if isinstance(res, Exception):
                server_name = list(sessions.keys())[i]
                logger.error(f"Failed to list prompts from server '{server_name}': {res}")
                continue
            for item in res:  # type: ignore
                all_prompts.append(item)
                p_name = item[1].name
                prompt_counts[p_name] = prompt_counts.get(p_name, 0) + 1

        final_prompts: List[Prompt] = []
        used_names = set()

        for server_name, prompt in all_prompts:
            original_name = prompt.name
            final_name = original_name

            if prompt_counts[original_name] > 1:
                final_name = f"{server_name}_{original_name}"

            base_final_name = final_name
            counter = 2
            while final_name in used_names:
                final_name = f"{base_final_name}_{counter}"
                counter += 1

            used_names.add(final_name)

            # Create a copy with the new name
            # Note: Pydantic models are immutable-ish, so we use model_copy
            new_prompt = prompt.model_copy(update={"name": final_name})
            final_prompts.append(new_prompt)

        return final_prompts
