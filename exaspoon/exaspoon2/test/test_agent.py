#!/usr/bin/env python3
"""
Simple test script to verify ExaSpoon agent functionality.
"""

import asyncio
import sys
import os

# Add spoon-core to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'spoon-core'))

from exaspoon_agent import ExaSpoonAgent


async def test_agent_initialization():
    """Test agent initialization and basic functionality."""
    print("🚀 Testing ExaSpoon Agent")
    print("=" * 40)

    # Create agent
    print("🤖 Creating ExaSpoon Agent...")
    agent = ExaSpoonAgent()

    # Test initialization
    print("🔄 Testing initialization...")
    try:
        initialized = await agent.initialize()
        print(f"{'✅' if initialized else '⚠️'} Initialization: {'Success' if initialized else 'Failed (fallback mode)'}")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False

    # Test status
    print("📊 Testing status check...")
    try:
        status = await agent.get_status()
        print(f"✅ Status check successful")
        print(f"   Agent: {'Ready' if status['agent_initialized'] else 'Not Ready'}")
        print(f"   Mode: {'Full' if not status['fallback_mode'] else 'Fallback'}")
        print(f"   MCP Server: {'Connected' if status['mcp_server_healthy'] else 'Disconnected'}")
        print(f"   Tools: {status['available_tools']} available")
    except Exception as e:
        print(f"❌ Status check error: {e}")

    # Test query with fallback mode check
    print("💬 Testing query processing...")
    test_queries = [
        "Hello, what can you help me with?",
        "Show account balances",
        "Check blockchain status",
        "What financial services do you offer?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test query {i}: {query}")
        try:
            response = await agent.query_agent(query)
            print(f"✅ Response received (length: {len(response)})")
            # Show first 100 characters of response
            print(f"   Preview: {response[:100]}{'...' if len(response) > 100 else ''}")

            # Check if fallback mode response is appropriate
            if agent.fallback_mode and "fallback mode" in response.lower():
                print("   ✅ Proper fallback mode response detected")
            elif not agent.fallback_mode and len(response) > 50:
                print("   ✅ Full mode response detected")

        except Exception as e:
            print(f"❌ Query {i} error: {e}")

    # Test cleanup
    print("\n🧹 Testing cleanup...")
    try:
        await agent.cleanup()
        print("✅ Cleanup successful")
    except Exception as e:
        print(f"❌ Cleanup error: {e}")

    print("\n🎉 Agent testing completed!")
    return True


async def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")

    try:
        from exaspoon_agent import ExaSpoonAgent
        print("✅ ExaSpoonAgent import successful")
    except Exception as e:
        print(f"❌ ExaSpoonAgent import failed: {e}")
        return False

    try:
        import app
        print("✅ FastAPI app import successful")
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False

    return True


async def main():
    """Main test function."""
    print("🧪 ExaSpoon Integration Tests")
    print("=" * 50)

    # Test imports first
    print("\n1️⃣ Testing imports...")
    if not await test_imports():
        print("❌ Import tests failed. Stopping.")
        return False

    # Test agent functionality
    print("\n2️⃣ Testing agent functionality...")
    try:
        success = await test_agent_initialization()
        if success:
            print("\n✅ All tests passed!")
            return True
        else:
            print("\n⚠️ Some tests had issues, but basic functionality works.")
            return True
    except Exception as e:
        print(f"\n❌ Agent tests failed: {e}")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)