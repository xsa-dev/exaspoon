"""On-chain/DeFi specialized agent."""

from __future__ import annotations

from spoon_ai.agents import SpoonReactAI
from spoon_ai.tools import ToolManager

from src.common.llm_client import LLMClient
from src.common.tools.mcp_tool_client import MCPToolClient
from src.common.tools.spoonos_style_base import load_prompt


class OnchainAgent(SpoonReactAI):
    """Handles DeFi-centric prompts."""

    def __init__(self, llm: LLMClient, mcp_client: MCPToolClient | None = None) -> None:
        system_prompt = load_prompt("onchain")

        # Initialize with MCP tools if available
        tool_manager = None
        if mcp_client:
            tool_manager = mcp_client.get_tool_manager()
            logger = __import__("logging").getLogger(__name__)
            logger.info(
                f"OnchainAgent initialized with {len(tool_manager.tools)} MCP tools"
            )

        super().__init__(
            llm=llm,
            system_prompt=system_prompt,
            available_tools=tool_manager or ToolManager([]),
        )

    async def run(self, request: str | None = None) -> str:
        lead = "For precise figures, request RPC/analytics."
        base_result = await super().run(request)
        return f"{base_result}\n\n{lead}"
