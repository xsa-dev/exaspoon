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


from src.common.llm_client import LLMClient
from src.mas.agents.subagents.analytics_agent import AnalyticsAgent


class FakeLLM(LLMClient):
    def __init__(self):
        # Initialize with dummy values
        super().__init__("fake-key", "gpt-3.5-turbo", "http://fake-url")

    def chat(self, *_: object, **__: object) -> str:
        return "stub"


class StubAnalyticsDb:
    def __init__(self) -> None:
        self.last_period: tuple[str, str] | None = None

    def get_tool_manager(self) -> MockToolManager:
        """Return empty tool manager for testing."""
        return MockToolManager([])

    def fetch_transactions_by_period(self, start, end):
        self.last_period = (start.isoformat(), end.isoformat())
        return [
            {"category_id": "cat-1", "currency": "RUB", "amount": 100},
            {"category_id": "cat-1", "currency": "RUB", "amount": 50},
            {"category_id": "cat-2", "currency": "USD", "amount": 10},
        ]

    def fetch_category_lookup(self):
        return {"cat-1": "utilities", "cat-2": "savings"}


class ErrorAnalyticsDb(StubAnalyticsDb):
    def fetch_transactions_by_period(
        self, *_: object, **__: object
    ):  # pragma: no cover - trivial override
        raise RuntimeError("boom")


def test_monthly_summary_rolls_up_amounts() -> None:
    import asyncio

    agent = AnalyticsAgent(FakeLLM(), StubAnalyticsDb())
    summary = asyncio.run(agent.get_monthly_summary(2024, 5))
    assert summary["utilities (RUB)"] == 150.0
    assert summary["savings (USD)"] == 10.0


def test_run_handles_supabase_errors() -> None:
    import asyncio

    agent = AnalyticsAgent(FakeLLM(), ErrorAnalyticsDb())
    result = asyncio.run(agent.run("summary for May 2024"))
    assert "Failed" in result
