"""Minimal base class shared by EXASPOON LLM-driven agents."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from spoon_ai.tools import ToolManager

from src.common.llm_client import LLMClient


def load_prompt(prompt_name: str) -> str:
    """Load prompt from prompts directory."""
    prompts_dir = (
        Path(__file__).resolve().parent.parent.parent.parent.parent / "prompts"
    )
    prompt_file = prompts_dir / f"{prompt_name}_prompt.md"
    if prompt_file.exists():
        return prompt_file.read_text(encoding="utf-8").strip()
    raise FileNotFoundError(f"Prompt file not found: {prompt_file}")


class ToolCallAgent:
    """Lightweight base that wraps repeated chat boilerplate.

    Can optionally use ToolManager for automatic tool calling support.
    """

    def __init__(
        self,
        llm: LLMClient,
        system_prompt: str,
        tool_manager: Optional[ToolManager] = None,
    ) -> None:
        self.llm = llm
        self.system_prompt = system_prompt
        self.tool_manager = tool_manager

    async def run(self, task: str | None = None) -> str:
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": task},
        ]

        # If tool_manager is provided, tools will be available for LLM
        # Note: LLMClient needs to support tool calling for this to work
        # Currently LLMClient uses LLMManager which should support tools
        result = await self.llm.chat(messages)
        return result
