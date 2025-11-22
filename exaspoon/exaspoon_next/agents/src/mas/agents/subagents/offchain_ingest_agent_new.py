"""Off-chain ingest agent using SpoonReactAI with automatic tool calling."""

from __future__ import annotations

from typing import Optional

from spoon_ai.agents import SpoonReactAI

from src.common.llm_client import LLMClient
from src.common.tools.mcp_tool_client import MCPToolClient
from src.common.tools.spoonos_style_base import load_prompt


class OffchainIngestAgent(SpoonReactAI):
    """Off-chain ingest agent with automatic MCP tool calling."""

    def __init__(self, llm: LLMClient, mcp_client: MCPToolClient) -> None:
        system_prompt = load_prompt("offchain_ingest")

        # Get tool manager with MCP tools
        tool_manager = mcp_client.get_tool_manager()

        # Initialize SpoonReactAI with tools
        super().__init__(
            llm=llm, system_prompt=system_prompt, tool_manager=tool_manager
        )

        self.mcp_client = mcp_client

    async def run(self, request: Optional[str] = None) -> str:
        """Process off-chain transaction request using automatic tool calling."""
        # SpoonReactAI will automatically call MCP tools as needed
        return await super().run(request)
