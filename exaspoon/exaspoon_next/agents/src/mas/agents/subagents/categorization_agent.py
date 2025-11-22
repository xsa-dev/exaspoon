"""Categorization agent using embeddings + LLM reasoning."""

from __future__ import annotations

from typing import Optional


from spoon_ai.agents import SpoonReactAI

from src.common.llm_client import LLMClient
from src.common.tools.mcp_tool_client import MCPToolClient
from src.common.tools.spoonos_style_base import load_prompt


class CategorizationAgent(SpoonReactAI):
    """LLM-based categorizer enriched with vector search hits."""

    def __init__(self, llm: LLMClient, db_client: MCPToolClient) -> None:
        system_prompt = load_prompt("categorization")
        # Initialize with tools from MCP client
        tool_manager = db_client.get_tool_manager()
        super().__init__(llm=llm, system_prompt=system_prompt, tools=tool_manager)
        self.db = db_client

    async def run(self, request: Optional[str] = None) -> str:
        """Let SpoonReactAI handle the categorization automatically using tools."""
        # The system prompt already contains the categorization instructions
        # SpoonReactAI will automatically use the available MCP tools
        return await super().run(request)
