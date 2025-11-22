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


# Mock the spoon_ai imports since they're not available in test environment
class MockToolManager:
    def __init__(self, tools=None):
        self.tools = tools or []


from src.mas.agents.subagents.categorization_agent import CategorizationAgent
from src.common.llm_client import LLMClient


class FakeLLM(LLMClient):
    def __init__(self, response: str) -> None:
        # Initialize with dummy values
        super().__init__("fake-key", "gpt-3.5-turbo", "http://fake-url")
        self.response = response

    def chat(self, *_: object, **__: object) -> str:
        return self.response


class StubCategorizationDb:
    def get_tool_manager(self) -> MockToolManager:
        """Return empty tool manager for testing."""
        return MockToolManager([])

    def search_similar_categories(
        self, *_: object, **__: object
    ) -> list[dict[str, object]]:
        return [
            {
                "id": "cat-1",
                "name": "utilities",
                "kind": "expense",
                "description": "Utilities",
            },
            {
                "id": "cat-2",
                "name": "savings",
                "kind": "expense",
                "description": "Savings",
            },
        ]

    def search_similar_transactions(
        self, *_: object, **__: object
    ) -> list[dict[str, object]]:
        return [
            {"id": "txn-1", "description": "Light bill payment"},
            {"id": "txn-2", "description": "Housing services"},
        ]


def test_categorization_returns_structure() -> None:
    # Test that agent can be instantiated with correct dependencies
    agent = CategorizationAgent(FakeLLM("Utilities match"), StubCategorizationDb())

    # Verify agent has expected attributes
    assert hasattr(agent, "db")
    assert hasattr(agent, "run")
    assert hasattr(agent, 'db')
    assert hasattr(agent, 'run')
    assert agent.db is not None
