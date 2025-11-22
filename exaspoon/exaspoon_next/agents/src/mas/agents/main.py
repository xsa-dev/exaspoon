"""Command-line interface for interacting with the EXASPOON graph agent."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from src.common.config import load_settings
from src.mas.agents.exaspoon_graph_agent import ExaSpoonGraphAgent

# Configure logging to show DEBUG level for LLMClient
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)


class TimeoutException(Exception):
    """Custom exception for operation timeouts."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutException("Operation timed out")


def main() -> None:
    settings = load_settings()
    # CLI intentionally runs without persisted memory so nothing is stored locally
    agent = ExaSpoonGraphAgent(settings, persist_session=True)
    
    print("EXASPOON CLI. Type 'exit' to quit.")
    print("⚠️  Operations have a 60-second timeout to prevent infinite loops.")
    
    # Set up signal handler for timeout (Unix systems only)
    if hasattr(signal, 'SIGALRM'):
        signal.signal(signal.SIGALRM, timeout_handler)
    
    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user_input or user_input.lower() in {"exit", "quit"}:
            break
        
        try:
            # Use ThreadPoolExecutor for timeout protection
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(agent.handle_user_message, user_input)
                try:
                    # 60-second timeout for each request
                    response = future.result(timeout=60)
                    
                    # Detect infinite loop patterns in response
                    if response and isinstance(response, str):
                        # Check for step loop pattern (Step 1, Step 2, etc.)
                        step_count = response.count("Step ")
                        if step_count >= 8:  # If we see 8+ steps, likely a loop
                            print("⚠️  Agent appears to be stuck in a loop (detected many steps).")
                            print("💡 Try a more specific request or check if tools are available.")
                            # Try to extract useful info from the loop
                            lines = response.split('\n')
                            for line in lines[-3:]:  # Show last few lines
                                if line.strip():
                                    print(f"📝 Last output: {line.strip()}")
                            continue
                    
                    # Check for error patterns
                    if "Stuck in loop" in response or "Resetting state" in response:
                        print("⚠️  Agent detected it was stuck and reset.")
                        print("💡 Try rephrasing your request.")
                        continue
                    
                    print(response)
                    
                except FutureTimeoutError:
                    print("⏰ Request timed out after 60 seconds. The agent may be stuck in a loop.")
                    print("💡 Try rephrasing your request or check if MCP server is running.")
                    # Cancel the future if it's still running
                    future.cancel()
                except Exception as exc:
                    print(f"error: {exc}")
                    # Check for specific infinite loop indicators
                    if "step" in str(exc).lower() and "10" in str(exc):
                        print("💡 This looks like an infinite loop. Try a simpler request.")
                        
        except TimeoutException:
            print("⏰ Request timed out. The agent may be stuck in a loop.")
            print("💡 Try rephrasing your request or check if MCP server is running.")
        except Exception as exc:  # pragma: no cover - CLI utility
            print(f"error: {exc}")
            continue


if __name__ == "__main__":
    main()
