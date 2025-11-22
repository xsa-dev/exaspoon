"""Async-only LLM client wrapper using spoon-core ChatBot."""

from __future__ import annotations

import logging
import os
from typing import Any, Iterable, List, Union

from spoon_ai.chat import ChatBot
from spoon_ai.schema import Message

logger = logging.getLogger(__name__)


class LLMClient(ChatBot):
    """Async-only LLM client wrapper using spoon-core ChatBot."""

    def __init__(
        self, api_key: str, model_name: str, base_url: str | None = None
    ) -> None:
        # Set environment variables for ChatBot
        os.environ["OPENAI_API_KEY"] = api_key
        if base_url:
            os.environ["OPENAI_BASE_URL"] = base_url

        # Disable other providers to avoid warnings
        os.environ.pop("OPENROUTER_API_KEY", None)
        os.environ.pop("DEEPSEEK_API_KEY", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ.pop("GEMINI_API_KEY", None)

        # Initialize ChatBot with LLMManager
        super().__init__(
            use_llm_manager=True, model_name=model_name, llm_provider="openai"
        )

        self._model = model_name
        self._api_key = api_key
        self._base_url = base_url

    async def chat(
        self, messages: Iterable[dict[str, str]], temperature: float = 0.2
    ) -> Any:
        """Async chat using ChatBot interface.

        This method maintains compatibility with existing code while using
        the new ChatBot interface from spoon-core.
        """
        logger.debug(
            f"[LLMClient.chat] Starting chat with model={self._model}, temperature={temperature}"
        )

        # Convert to list and validate format
        messages_list = []
        original_messages = list(messages)
        logger.debug(
            f"[LLMClient.chat] Received {len(original_messages)} input messages"
        )

        for idx, msg in enumerate(original_messages):
            logger.debug(
                f"[LLMClient.chat] Processing message {idx}: type={type(msg)}, value={msg}"
            )

            # Ensure message is a dict with 'role' and 'content' keys
            if isinstance(msg, dict):
                # Validate required fields
                role = msg.get("role")
                content = msg.get("content")
                logger.debug(
                    f"[LLMClient.chat] Message {idx} dict keys: {list(msg.keys())}, role={role}, content_type={type(content)}"
                )

                if role is None or content is None:
                    logger.warning(
                        f"[LLMClient.chat] Skipping malformed message {idx}: missing role or content"
                    )
                    continue

                # Copy entire dict to preserve all fields (tool_calls, function_call, etc.)
                # and ensure role and content are strings
                normalized_msg = dict(msg)  # Copy to preserve all fields
                normalized_msg["role"] = str(role)
                normalized_msg["content"] = str(content)
                logger.debug(
                    f"[LLMClient.chat] Normalized message {idx}: keys={list(normalized_msg.keys())}, role={normalized_msg['role']}"
                )
                messages_list.append(normalized_msg)
            else:
                # If it's not a dict, convert to a simple user message
                logger.warning(
                    f"[LLMClient.chat] Message {idx} is not a dict, converting to user message"
                )
                messages_list.append({"role": "user", "content": str(msg)})

        if not messages_list:
            logger.error("[LLMClient.chat] No valid messages after processing")
            raise ValueError("No valid messages provided")

        logger.info(
            f"[LLMClient.chat] Prepared {len(messages_list)} messages for ChatBot"
        )
        logger.debug(
            f"[LLMClient.chat] Messages to send: {[repr(msg) for msg in messages_list]}"
        )

        try:
            # Call ChatBot.ask() with messages directly
            logger.debug(
                f"[LLMClient.chat] Calling ChatBot.ask() with {len(messages_list)} messages"
            )
            response = await super().ask(messages_list)
            logger.debug(
                f"[LLMClient.chat] ChatBot.chat() returned: type={type(response)}, value={response}"
            )
            
            # Handle different response types - return proper object for compatibility
            logger.debug(
                f"[LLMClient.chat] Processing response: type={type(response)}"
            )
            # Return the original response object for SpoonReactAI compatibility
            return response
        except Exception as e:
            logger.error(
                f"[LLMClient.chat] Error calling ChatBot.chat(): {type(e).__name__}: {e}"
            )
            logger.error(
                f"[LLMClient.chat] Messages that caused error: {messages_list}"
            )
            raise

    async def ask_tool(
        self,
        messages: List[Union[dict, Message]],
        system_msg: str | None = None,
        tools: list[dict] | None = None,
        tool_choice: str | None = None,
        output_queue: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Async ask_tool method using ChatBot interface with defensive tools handling.
        
        This method ensures the tools parameter is always a valid list to prevent
        API errors when agents have no tools.
        """
        logger.debug(
            f"[LLMClient.ask_tool] Starting with model={self._model}, tools_type={type(tools)}, tools_value={tools}"
        )
        
        # Defensive check: ensure tools is always a list, never None or dict
        if tools is None:
            tools = []
            logger.debug("[LLMClient.ask_tool] tools was None, converted to empty list")
        elif isinstance(tools, dict):
            # This should not happen, but let's handle it defensively
            if not tools:  # Empty dict
                tools = []
                logger.warning("[LLMClient.ask_tool] tools was empty dict, converted to empty list")
            else:
                # Convert dict values to list if it looks like a tool collection
                tools = list(tools.values()) if all(isinstance(v, dict) for v in tools.values()) else []
                logger.warning(f"[LLMClient.ask_tool] tools was dict, converted to list with {len(tools)} items")
        elif not isinstance(tools, list):
            # Convert any other type to empty list
            tools = []
            logger.warning(f"[LLMClient.ask_tool] tools was unexpected type {type(tools)}, converted to empty list")
        
        # Ensure all tools in the list are valid dict objects
        valid_tools = []
        for i, tool in enumerate(tools):
            if isinstance(tool, dict):
                valid_tools.append(tool)
            else:
                logger.warning(f"[LLMClient.ask_tool] Tool {i} is not a dict: {type(tool)}, skipping")
        
        logger.info(
            f"[LLMClient.ask_tool] Prepared {len(valid_tools)} valid tools for ChatBot.ask_tool"
        )
        
        # Convert messages to list format
        messages_list = list(messages)
        logger.debug(
            f"[LLMClient.ask_tool] Calling ChatBot.ask_tool() with {len(messages_list)} messages and {len(valid_tools)} tools"
        )
        
        try:
            # If no valid tools, use regular chat instead of ask_tool to avoid API issues
            if not valid_tools:
                logger.debug("[LLMClient.ask_tool] No valid tools, using chat() instead of ask_tool()")
                response = await super().ask(messages_list, system_msg=system_msg, output_queue=output_queue, **kwargs)
                # Convert to LLMResponse-like object for SpoonReactAI compatibility
                from spoon_ai.schema import LLMResponse
                if hasattr(response, 'content'):
                    # Already has content, just ensure tool_calls exists
                    if not hasattr(response, 'tool_calls'):
                        response.tool_calls = []
                    return response
                else:
                    # Convert string to LLMResponse
                    return LLMResponse(
                        content=str(response),
                        tool_calls=[],
                        finish_reason="stop"
                    )
            
            # Call ChatBot.ask_tool() with validated parameters
            call_kwargs = {
                "messages": messages_list,
                "system_msg": system_msg,
                "output_queue": output_queue,
                "tools": valid_tools,
            }
            
            # Only include tool_choice if we have valid tools
            if tool_choice:
                call_kwargs["tool_choice"] = tool_choice
                logger.debug(f"[LLMClient.ask_tool] Including tool_choice: {tool_choice}")
            
            logger.debug(f"[LLMClient.ask_tool] Calling ask_tool with {len(valid_tools)} tools")
            response = await super().ask_tool(**call_kwargs)
            logger.debug(
                f"[LLMClient.ask_tool] ChatBot.ask_tool() returned: type={type(response)}"
            )
            return response
        except Exception as e:
            logger.error(
                f"[LLMClient.ask_tool] Error calling ChatBot.ask_tool(): {type(e).__name__}: {e}"
            )
            logger.error(
                f"[LLMClient.ask_tool] Tools that caused error: {valid_tools}"
            )
            raise

    # Alias for backward compatibility
    achat = chat

    async def embed(
        self, text: str, model: str = "text-embedding-3-large"
    ) -> list[float]:
        """Async embedding using ChatBot."""
        if not text.strip():
            return []

        logger.debug(f"[LLMClient.embed] Starting embedding with model={model}")

        try:
            # Use OpenAI client directly for embeddings since ChatBot doesn't have embed method
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self._api_key, base_url=self._base_url)
            response = await client.embeddings.create(model=model, input=text)
            result = response.data[0].embedding
            logger.debug(f"[LLMClient.embed] Embedding completed, length={len(result)}")
            return result
        except Exception as e:
            logger.error(
                f"[LLMClient.embed] Error creating embedding: {type(e).__name__}: {e}"
            )
            raise
