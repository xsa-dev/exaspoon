#!/usr/bin/env python3
"""Simple test of ExaSpoon system without SpoonReactAI."""

import asyncio
import os

from src.common.config import load_settings
from src.common.llm_client import LLMClient


async def test_simple_chat():
    """Test simple LLM chat without tools."""
    settings = load_settings()

    print(f"API Key: {settings.openai_api_key[:20]}...")
    print(f"Base URL: {settings.openai_base_url}")
    print(f"Model: {settings.model_name}")

    llm = LLMClient(
        settings.openai_api_key, settings.model_name, settings.openai_base_url
    )

    # Test simple chat
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that responds in English.",
        },
        {"role": "user", "content": "Hello! How are you?"},
    ]

    try:
        response = await llm.chat(messages)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_simple_chat())
