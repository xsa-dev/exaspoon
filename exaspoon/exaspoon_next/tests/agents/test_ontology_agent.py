from __future__ import annotations

import os
import sys

# Add agents directory to path
agents_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "agents")
)
sys.path.insert(0, agents_dir)
sys.path.insert(0, os.path.join(agents_dir, "src"))

from typing import Optional

# Import real ToolManager for proper type checking
from spoon_ai.tools import ToolManager

from src.common.llm_client import LLMClient
from src.mas.agents.subagents.ontology_agent import OntologyAgent


class FakeLLM(LLMClient):
    def __init__(self, response: str) -> None:
        super().__init__("fake-key", "gpt-3.5-turbo", "http://fake-url")
        self.response = response

    def chat(self, *_: object, **__: object) -> str:
        return self.response


class StubOntologyDb:
    def __init__(self) -> None:
        self.last_search: dict[str, object] | None = None

    def get_tool_manager(self) -> ToolManager:
        """Return a mock tool manager for testing."""
        return ToolManager([])

    def search_categories(self, query: str) -> list[dict[str, object]]:
        self.last_search = {"query": query}
        return [
            {"id": "cat-1", "name": "food", "kind": "expense"},
            {"id": "cat-2", "name": "transport", "kind": "expense"},
            {"id": "cat-3", "name": "salary", "kind": "income"},
        ]

    def search_accounts(self, query: str) -> list[dict[str, object]]:
        self.last_search = {"query": query}
        return [
            {"id": "acc-1", "name": "Sberbank Card", "type": "offchain"},
            {"id": "acc-2", "name": "NEO Wallet", "type": "onchain"},
        ]


def test_ontology_agent_initializes_without_tools() -> None:
    """Test that OntologyAgent initializes correctly."""
    agent = OntologyAgent(FakeLLM("structured response"))

    # Verify agent has expected attributes
    assert hasattr(agent, "run")
    assert agent is not None
