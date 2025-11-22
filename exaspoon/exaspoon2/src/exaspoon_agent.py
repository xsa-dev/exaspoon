#!/usr/bin/env python3
"""
ExaSpoon MCP Agent

Persona-aligned agent that demonstrates MCP tool calls while
speaking in the ExaSpoon (AI Financial Samurai) style.
"""

import asyncio
import logging
import os

from spoon_ai.agents import SpoonReactMCP
from spoon_ai.chat import ChatBot
from spoon_ai.graph.checkpointer import InMemoryCheckpointer
from spoon_ai.llm.manager import LLMManager
from spoon_ai.memory.short_term_manager import MessageTokenCounter
from spoon_ai.tools.mcp_tool import MCPTool
from spoon_ai.tools.tool_manager import ToolManager

# Configure logging - reduce output
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class ExaSpoonAgent:
    """Persona-aligned MCP agent using the ExaSpoon style"""

    def __init__(self):
        # Use the ExaSpoon persona (AI Financial Samurai)
        self.persona_name = "exaspoon"
        self.agent = None
        self.llm_manager = None
        self.chatbot = None
        self.fallback_mode = False  # For simple MCP tool calls

    async def initialize(self):
        """Initialize the agent with MCP tools"""
        try:
            # Initialize LLM Manager
            self.llm_manager = LLMManager()

            # Initialize memory
            from spoon_ai.memory.short_term_manager import (
                ShortTermMemoryManager,
                TrimStrategy,
            )

            checkpointer = InMemoryCheckpointer(
                ttl_seconds=60 * 60,  # one hour
                max_checkpoints_per_thread=100,
                max_threads=10,
            )
            token_counter = MessageTokenCounter()
            memory_manager = ShortTermMemoryManager(
                checkpointer=checkpointer,
                token_counter=token_counter,
                default_trim_strategy=TrimStrategy.FROM_END,
            )

            # Initialize ChatBot
            self.chatbot = ChatBot(
                llm_manager=self.llm_manager,
                enable_short_term_memory=True,
                short_term_memory_manager=memory_manager,
            )

            # Initialize tools
            managed_tools = await self.initialize_tools()

            # Check MCP server health before creating agent
            mcp_gateway_host = os.getenv("MCP_GATEWAY_HOST", "127.0.0.1")
            mcp_gateway_port = os.getenv("MCP_GATEWAY_PORT", "8766")
            mcp_healthy = await self._check_mcp_server_health(
                f"http://{mcp_gateway_host}:{mcp_gateway_port}/mcp"
            )

            if not mcp_healthy:
                logger.warning("⚠️ MCP server is not available, enabling fallback mode")
                self.fallback_mode = True
                # Don't create SpoonReactMCP agent when MCP is unavailable
                # This prevents the tools parameter error
                logger.info(
                    "✅ Agent initialized in fallback mode (MCP server unavailable)"
                )
                return True

            # Create agent with both MCP tools (only if MCP server is healthy)
            # Ensure we have proper ToolManager with empty list if no tools available
            if managed_tools is None or (
                hasattr(managed_tools, "tools") and len(managed_tools.tools) == 0
            ):
                logger.info("🔄 No MCP tools available, creating agent without tools")
                # Create agent with empty tools list
                self.agent = SpoonReactMCP(
                    name="exaspoon_agent",
                    description="ExaSpoon MCP agent for financial analysis",
                    llm_manager=self.llm_manager,
                    tools=[],  # Empty list instead of empty ToolManager
                    persona_name=self.persona_name,
                )
            else:
                self.agent = SpoonReactMCP(
                    name="exaspoon_agent",
                    description="ExaSpoon MCP agent for financial analysis",
                    llm_manager=self.llm_manager,
                    tools=managed_tools,
                    persona_name=self.persona_name,
                )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize ExaSpoon MCP Agent: {e}")
            # Try to initialize in fallback mode
            logger.info("🔄 Attempting to initialize in fallback mode...")
            try:
                # Initialize just LLM manager and tools
                self.llm_manager = LLMManager()
                self.fallback_mode = True
                logger.info("✅ Initialized in fallback mode (no SpoonReactMCP)")
                return True
            except Exception as fallback_e:
                logger.error(f"❌ Fallback mode also failed: {fallback_e}")
                return False

    def _validate_mcp_config(self, config: dict) -> bool:
        """Validate MCP server configuration."""
        try:
            # Check required fields
            required_fields = ["name", "description", "mcp_server"]
            for field in required_fields:
                if field not in config:
                    logger.error(f"❌ Missing required field in MCP config: {field}")
                    return False

            mcp_server = config["mcp_server"]
            if not isinstance(mcp_server, dict):
                logger.error("❌ MCP server configuration must be a dictionary")
                return False

            # Check MCP server required fields
            server_required = ["url", "transport"]
            for field in server_required:
                if field not in mcp_server:
                    logger.error(
                        f"❌ Missing required field in mcp_server config: {field}"
                    )
                    return False

            # Validate URL format
            url = mcp_server["url"]
            if not url.startswith(("http://", "https://")):
                logger.error(f"❌ Invalid MCP server URL format: {url}")
                return False

            # Validate transport method
            transport = mcp_server["transport"]
            if transport not in ["http", "websocket", "stdio"]:
                logger.error(f"❌ Unsupported transport method: {transport}")
                return False

            # Validate timeout
            timeout = mcp_server.get("timeout", 30)
            if not isinstance(timeout, int) or timeout <= 0:
                logger.error(f"❌ Invalid timeout value: {timeout}")
                return False

            logger.info("✅ MCP configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"❌ MCP configuration validation failed: {e}")
            return False

    async def _check_mcp_server_health(self, url: str, timeout: int = 5) -> bool:
        """Check if MCP server is responsive."""
        try:
            import httpx

            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                is_healthy = response.status_code < 500
                logger.info(
                    f"🏥 MCP server health check: {'✅ Healthy' if is_healthy else '❌ Unhealthy'}"
                )
                return is_healthy
        except Exception as e:
            logger.warning(f"⚠️ MCP server health check failed: {e}")
            return False

    async def initialize_tools(self):
        """Initialize MCP tools with proper error handling and configuration."""
        try:
            # Create Python MCP server configuration
            mcp_gateway_host = os.getenv("MCP_GATEWAY_HOST", "127.0.0.1")
            mcp_gateway_port = os.getenv("MCP_GATEWAY_PORT", "8766")

            mcp_config = {
                "name": "exaspoon_mcp_server",
                "type": "mcp",
                "description": "ExaSpoon MCP server for financial analysis",
                "enabled": True,
                "mcp_server": {
                    "url": f"http://{mcp_gateway_host}:{mcp_gateway_port}/mcp",
                    "transport": "http",
                    "timeout": 30,
                    "headers": {
                        "User-Agent": "SpoonOS-HTTP-MCP/1.0",
                        "Accept": "application/json",
                    },
                },
            }

            # Validate configuration
            if not self._validate_mcp_config(mcp_config):
                raise ValueError("Invalid MCP server configuration")

            # Log configuration (without sensitive data)
            logger.info(f"🔧 Initializing MCP tools for: {mcp_config['name']}")
            logger.info(f"🌐 MCP server URL: {mcp_config['mcp_server']['url']}")

            # Quick health check before proceeding
            mcp_url = mcp_config["mcp_server"]["url"]
            mcp_timeout = mcp_config["mcp_server"]["timeout"]

            if not await self._check_mcp_server_health(mcp_url, mcp_timeout):
                logger.warning(
                    f"⚠️ MCP server at {mcp_url} is not responding, but proceeding with initialization"
                )

            # Create MCP tools (without pre-loading parameters)
            exaspoon_mcp_server = MCPTool(
                name=mcp_config["name"],
                description=mcp_config["description"],
                mcp_config=mcp_config["mcp_server"],
            )

            logger.info("🔧 Fetching available tools from MCP server...")
            tool_list = await exaspoon_mcp_server.list_available_tools()
            logger.info(f"📋 Found {len(tool_list)} tools available")

            # Convert dictionaries to MCPTool objects
            mcp_tools = []
            for tool_dict in tool_list:
                try:
                    mcp_tool = MCPTool(
                        name=tool_dict["name"],
                        description=tool_dict.get("description", ""),
                        parameters=tool_dict.get("inputSchema"),
                        mcp_config=exaspoon_mcp_server.mcp_config,
                    )
                    mcp_tools.append(mcp_tool)
                except Exception as tool_e:
                    logger.warning(
                        f"⚠️ Failed to create tool {tool_dict.get('name', 'unknown')}: {tool_e}"
                    )
                    continue

            logger.info(f"✅ Successfully initialized {len(mcp_tools)} MCP tools")
            return ToolManager(mcp_tools)

        except Exception as e:
            logger.error(f"❌ Failed to initialize MCP tools: {e}")
            # Return empty tool manager as fallback
            logger.info("🔄 Returning empty ToolManager as fallback")
            return ToolManager([])

    async def query_agent(self, question: str):
        """Query the agent with a question (agent will call MCP tools as needed)"""
        if not question or not question.strip():
            return "❌ Please provide a valid question or request."

        question = question.strip()

        try:
            if self.fallback_mode:
                # Enhanced fallback response
                return f"""🤖 ExaSpoon Agent (Fallback Mode)

Your query: {question}

I'm currently running in fallback mode due to initialization issues. However, I can still help you with financial tasks:

📊 Available capabilities:
- Transaction management and analysis
- Account management and monitoring
- Budget planning and expense tracking
- Financial reporting and insights

💡 To get full functionality with MCP tools:
1. Ensure the MCP server is running on ${MCP_GATEWAY_HOST}:${MCP_GATEWAY_PORT}
2. Try reinitializing the agent
3. Check the logs for any initialization errors

🔧 Available tools when fully operational:
- Neo blockchain operations (balance, transactions, blocks)
- Solana blockchain operations (wallet, transfers, swaps)
- Cross-chain analysis and comparison
- Real-time price data and market analysis

Would you like me to try reinitializing, or do you have a specific financial task I can assist with?"""

            logger.info(f"🔄 Processing query: {question[:100]}...")
            result = await self.agent.run(question)

            if not isinstance(result, str):
                logger.warning(f"⚠️ Agent returned non-string result: {type(result)}")
                return f"❌ Agent returned unexpected result type: {type(result)}"

            logger.info("✅ Query processed successfully")
            return result

        except asyncio.TimeoutError:
            error_msg = "⏰ Query processing timed out. Please try again with a simpler request."
            logger.error(error_msg)
            return error_msg

        except ConnectionError as e:
            error_msg = (
                f"🔌 Connection error: {str(e)}. Please check if MCP server is running."
            )
            logger.error(error_msg)
            return error_msg

        except Exception as e:
            error_msg = f"❌ Agent execution failed: {str(e)}"
            logger.error(f"❌ Query failed: {e}")
            return error_msg

    async def get_status(self) -> dict:
        """Get agent and MCP server status."""
        mcp_gateway_host = os.getenv("MCP_GATEWAY_HOST", "127.0.0.1")
        mcp_gateway_port = os.getenv("MCP_GATEWAY_PORT", "8766")

        status = {
            "agent_initialized": self.agent is not None,
            "fallback_mode": self.fallback_mode,
            "llm_manager_available": self.llm_manager is not None,
            "mcp_server_url": f"http://{mcp_gateway_host}:{mcp_gateway_port}/mcp",
            "timestamp": asyncio.get_event_loop().time()
            if asyncio.get_event_loop()
            else None,
        }

        # Check MCP server health
        try:
            status["mcp_server_healthy"] = await self._check_mcp_server_health(
                status["mcp_server_url"]
            )
        except Exception as e:
            status["mcp_server_healthy"] = False
            status["mcp_server_error"] = str(e)

        # Count available tools
        if (
            self.agent
            and hasattr(self.agent, "tools")
            and hasattr(self.agent.tools, "tools")
        ):
            status["available_tools"] = len(self.agent.tools.tools)
        else:
            status["available_tools"] = 0

        return status

    async def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("🧹 Starting cleanup process...")

            # Cleanup agent
            if self.agent:
                if hasattr(self.agent, "cleanup"):
                    await self.agent.cleanup()
                    logger.info("✅ Agent cleanup completed")
                self.agent = None

            # Cleanup LLM manager
            if self.llm_manager:
                if hasattr(self.llm_manager, "cleanup"):
                    await self.llm_manager.cleanup()
                    logger.info("✅ LLM manager cleanup completed")
                self.llm_manager = None

            # Cleanup chatbot
            if self.chatbot:
                if hasattr(self.chatbot, "cleanup"):
                    await self.chatbot.cleanup()
                    logger.info("✅ Chatbot cleanup completed")
                self.chatbot = None

            logger.info("✅ All cleanup operations completed")

        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            raise


async def main():
    """Main demo function"""
    print("🚀 ExaSpoon MCP Agent - Financial Samurai")
    print("=" * 60)
    print("AI-powered financial agent with blockchain capabilities.")
    print("Demonstrates MCP tool integration for Neo, Solana, and DeFi operations.")
    print()

    # Create and initialize agent
    print("🤖 Creating ExaSpoon Agent...")
    agent = ExaSpoonAgent()

    # Initialize agent with status feedback
    print("🔄 Initializing agent and connecting to MCP server...")
    if not await agent.initialize():
        print("❌ Agent initialization failed. Stopping demo.")
        return

    # Show initialization status
    status = await agent.get_status()
    print(f"\n📊 Initialization Status:")
    print(f"   ✅ Agent: {'Ready' if status['agent_initialized'] else 'Not Ready'}")
    print(
        f"   {'✅' if not status['fallback_mode'] else '⚠️'} Mode: {'Full' if not status['fallback_mode'] else 'Fallback'}"
    )
    print(
        f"   {'✅' if status['mcp_server_healthy'] else '❌'} MCP Server: {'Connected' if status['mcp_server_healthy'] else 'Disconnected'}"
    )
    print(f"   📚 Available Tools: {status['available_tools']}")

    if not status["mcp_server_healthy"] and not status["fallback_mode"]:
        print(
            "\n⚠️ Warning: MCP server is not responding. Some features may be limited."
        )
        mcp_gateway_host = os.getenv("MCP_GATEWAY_HOST", "localhost")
        mcp_gateway_port = os.getenv("MCP_GATEWAY_PORT", "8766")
        print(
            f"   Ensure the MCP server is running on {mcp_gateway_host}:{mcp_gateway_port}"
        )

    # Interactive demo
    print("\n💬 Interactive Financial Assistant")
    print("Ask questions and the agent will call MCP tools automatically.")
    print("\n🎯 Example Queries:")
    print("   💰 'Show account balances for Neo blockchain'")
    print("   🔍 'Analyze Solana wallet XYZ'")
    print("   📊 'Get latest gas prices and network stats'")
    print("   💱 'Compare Neo vs Solana transaction fees'")
    print("   📈 'Show recent DeFi trading activity'")
    print("   🏦 'Analyze portfolio performance'")
    print("\n🛑 Commands: 'quit', 'exit', 'status', 'help'")

    while True:
        try:
            user_input = input("\n💬 Your query: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                break
            elif user_input.lower() == "status":
                status = await agent.get_status()
                print(f"\n📊 Current Status:")
                print(
                    f"   Agent: {'✅ Ready' if status['agent_initialized'] else '❌ Not Ready'}"
                )
                print(
                    f"   Mode: {'🟢 Full' if not status['fallback_mode'] else '🟡 Fallback'}"
                )
                print(
                    f"   MCP Server: {'🟢 Connected' if status['mcp_server_healthy'] else '🔴 Disconnected'}"
                )
                print(f"   Tools: {status['available_tools']} available")
                continue
            elif user_input.lower() == "help":
                print(f"\n📖 ExaSpoon Agent Help:")
                print(f"   • Ask about blockchain operations (Neo, Solana)")
                print(f"   • Request financial analysis and market data")
                print(f"   • Query transaction details and wallet balances")
                print(f"   • Get network statistics and gas prices")
                print(f"   • Type 'status' to check agent health")
                print(f"   • Type 'quit' to exit")
                continue
            elif not user_input:
                continue

            print("🔄 Processing your request...")
            result = await agent.query_agent(user_input)
            print(f"\n🤖 ExaSpoon Response:")
            print(f"{'─' * 50}")
            print(result)
            print(f"{'─' * 50}")

        except KeyboardInterrupt:
            print("\n\n🛑 Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("💡 Try 'status' to check agent health or 'help' for examples")

    # Cleanup
    print("\n🧹 Shutting down gracefully...")
    await agent.cleanup()
    print("✅ Thank you for using ExaSpoon Agent!")
    print("🎯 Stay financially disciplined and keep building!")


if __name__ == "__main__":
    console = True
    if console:
        asyncio.run(main())
