"""Ontology agent responsible for reasoning about EXASPOON domain objects."""

from __future__ import annotations

from typing import Any, Dict

from spoon_ai.agents import SpoonReactAI
from spoon_ai.tools import ToolManager

from src.common.llm_client import LLMClient
from src.common.tools.mcp_tool_client import MCPToolClient
from src.common.tools.spoonos_style_base import load_prompt


class OntologyAgent(SpoonReactAI):
    """Converts free-form language into structured EXASPOON vocabulary."""

    def __init__(self, llm: LLMClient, mcp_client: MCPToolClient | None = None) -> None:
        system_prompt = load_prompt("ontology")

        # Ontology agent typically doesn't need tools, but we'll support them if provided
        tool_manager = None
        if mcp_client:
            tool_manager = mcp_client.get_tool_manager()

        super().__init__(
            llm=llm,
            system_prompt=system_prompt,
            available_tools=tool_manager or ToolManager([]),
        )

    async def run(self, request: str | None = None) -> str:
        """Let SpoonReactAI handle ontology reasoning automatically."""
        return await super().run(request)

    async def summarize_entities(self, text: str) -> str:
        prompt = (
            "Create a brief description of key entities (Accounts, Transactions,"
            " Categories) based on the text. Format: JSON with lists."
        )
        messages = [
            {"role": "system", "content": f"{self.system_prompt}\n{prompt}"},
            {"role": "user", "content": text},
        ]
        result = await self.llm.ask(messages)  # type: ignore[arg-type]
        return result

    def normalize_transaction(self, payload: Dict[str, Any]) -> str:
        """Return a normalized textual description of a transaction payload."""
        description = (
            "Describe the transaction in natural language, using the fields:"
            " amount, currency, direction, occurred_at, description."
        )
        messages = [
            {"role": "system", "content": f"{self.system_prompt}\n{description}"},
            {"role": "user", "content": str(payload)},
        ]
        # Use sync call for this method since it's not part of run() flow
        import asyncio

        try:
            asyncio.get_running_loop()
            # In async context, run in thread
            import concurrent.futures

            def run_sync():
                return asyncio.run(self.llm.ask(messages))  # type: ignore[arg-type]

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_sync)
                return future.result()
        except RuntimeError:
            # No event loop, use asyncio.run
            return asyncio.run(self.llm.ask(messages))  # type: ignore[arg-type]
