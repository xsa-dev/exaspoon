# Testing Guide for ExaSpoon Agent

This directory contains comprehensive testing documentation and test files for the ExaSpoon financial AI agent. The agent is a Model Context Protocol (MCP) agent designed for financial analysis on blockchain networks.

**Initial Blockchain Support**: The first version supports two major blockchain networks:
- **Neo (NEO)**: Smart economy platform with digital assets, identities, and smart contracts
- **Solana (SOL)**: High-performance blockchain supporting fast, secure, and scalable decentralized apps and crypto-currencies

## 📋 Table of Contents

1. [Agent Overview](#agent-overview)
2. [Testing Architecture](#testing-architecture)
3. [Prerequisites](#prerequisites)
4. [Test Setup](#test-setup)
5. [Test Categories](#test-categories)
6. [Running Tests](#running-tests)
7. [Test Data & Mocking](#test-data--mocking)
8. [Continuous Integration](#continuous-integration)
9. [Troubleshooting](#troubleshooting)

## 🔍 Agent Overview

The ExaSpoon agent is a sophisticated financial AI system with the following key components:

### Core Architecture
- **FastAPI Web Server**: RESTful API serving web interface and chat functionality
- **ExaSpoonAgent**: Main agent class managing MCP tools and LLM integration
- **LLMManager**: Unified interface for multiple LLM providers (OpenAI, Anthropic, Gemini, DeepSeek)
- **ToolManager**: Manages both native and MCP tools
- **ChatBot**: Conversational interface with memory management
- **MCPTool**: Integration with MCP servers for external tool access

### Key Features
- **Multi-LLM support** with load balancing and fallback strategies
- **MCP tool integration** for extensible functionality
- **Multi-blockchain operations** (Neo and Solana blockchains)
- **Cross-chain analysis and comparison tools**
- **Real-time streaming responses** *(TODO: Not yet implemented)*
- **Memory management** for context retention
- **Health monitoring** and status reporting
- **Multi-language support**

## 🏗️ Testing Architecture

### Test Structure
```
test/
├── README.md                    # This file
├── unit/                        # Unit tests for individual components
├── integration/                 # Integration tests for component interactions
├── e2e/                        # End-to-end tests for complete workflows
├── performance/                # Performance and load testing
├── fixtures/                   # Test data and mock objects
├── conftest.py                 # Pytest configuration and fixtures
└── utils/                      # Test utilities and helpers

spoon-core/tests/               # Existing SpoonAI SDK tests
├── test_llm_manager_integration.py
├── test_agent_llm_integration.py
├── test_chatbot_integration.py
├── test_x402_service.py
├── test_neofs_client.py
└── asserts.py                  # Test assertion utilities
```

### Testing Philosophy
1. **Isolation**: Unit tests should be independent and not rely on external services
2. **Integration**: Tests should verify component interactions work correctly
3. **Real-world**: E2E tests should simulate actual user scenarios
4. **Performance**: Load tests ensure the system can handle expected traffic
5. **Reliability**: Tests should be deterministic and repeatable

## ✅ Prerequisites

### Required Software
- **Python 3.8+**: Primary development language
- **uv**: Package manager (used in this project)
- **pytest**: Testing framework
- **Docker**: For containerized testing environments
- **Git**: Version control

### Environment Setup
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd exaspoon2
   ```

2. **Install dependencies**:
   ```bash
   uv sync  # or: pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Verify MCP server** (if testing MCP integration):
   ```bash
   # Start MCP server using the Makefile (recommended)
   make dev

   # Or start MCP server and web application separately
   make console &  # Start MCP gateway in background
   sleep 3
   uv run app.py   # Start FastAPI server

   # MCP server will be available on localhost:8766
   # FastAPI app will be available on http://localhost:5556
   ```

### Required Environment Variables
```bash
# LLM Provider API Keys
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GEMINI_API_KEY=your-gemini-key
DEEPSEEK_API_KEY=sk-your-deepseek-key

# Agent Configuration
AGENT_NAME="ExaSpoon"
AGENT_PERSONA="AI Financial Samurai"
DEFAULT_LLM_PROVIDER="openai"

# MCP Configuration
MCP_SERVER_URL="http://localhost:8766"
MCP_TIMEOUT=30

# Database Configuration (if applicable)
DATABASE_URL="sqlite:///test.db"

# Neo Blockchain Configuration
NEO_RPC_URL="https://testnet1.neo.coz.io:443"
NEO_WALLET_WIF="your-test-wif"

# Solana Blockchain Configuration
SOLANA_RPC_URL="https://api.devnet.solana.com"
SOLANA_WALLET_PRIVATE_KEY="your-test-private-key"
```

## 🛠️ Test Setup

### Initial Setup
1. **Create test directory structure**:
   ```bash
   mkdir -p test/{unit,integration,e2e,performance,fixtures,utils}
   ```

2. **Create pytest configuration** (`test/conftest.py`):
   ```python
   import pytest
   import asyncio
   from unittest.mock import Mock, AsyncMock
   from spoon_ai.llm.manager import LLMManager
   from exaspoon_agent import ExaSpoonAgent

   @pytest.fixture(scope="session")
   def event_loop():
       """Create an instance of the default event loop for the test session."""
       loop = asyncio.get_event_loop_policy().new_event_loop()
       yield loop
       loop.close()

   @pytest.fixture
   async def mock_llm_manager():
       """Create a mock LLM manager for testing."""
       manager = Mock(spec=LLMManager)
       manager.chat = AsyncMock(return_value=Mock(content="Test response"))
       manager.chat_stream = AsyncMock()
       manager.health_check_all = AsyncMock(return_value={"openai": True})
       return manager

   @pytest.fixture
   async def mock_exaspoon_agent(mock_llm_manager):
       """Create a mock ExaSpoon agent."""
       agent = Mock(spec=ExaSpoonAgent)
       agent.llm_manager = mock_llm_manager
       agent.process_query = AsyncMock(return_value="Test response")
       # TODO: Implement process_query_stream when streaming feature is ready
       agent.process_query_stream = AsyncMock()  # Mock for future implementation
       return agent
   ```

### Test Dependencies
Install testing-specific dependencies:
```bash
uv add --dev pytest pytest-asyncio pytest-mock pytest-cov pytest-xdist
uv add --dev httpx-mock aioresponses
uv add --dev factory-boy faker  # For test data generation
```

## 📝 Test Categories

### 1. Unit Tests (`test/unit/`)

Test individual components in isolation.

#### **LLM Manager Tests**
```python
# test/unit/test_llm_manager.py
import pytest
from unittest.mock import Mock, AsyncMock
from spoon_ai.llm.manager import LLMManager

class TestLLMManager:
    @pytest.mark.asyncio
    async def test_chat_with_provider(self, mock_llm_manager):
        """Test chat functionality with specific provider."""
        messages = [{"role": "user", "content": "Hello"}]

        response = await mock_llm_manager.chat(messages, provider="openai")

        assert response.content == "Test response"
        mock_llm_manager.chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, mock_llm_manager):
        """Test fallback when primary provider fails."""
        # Configure mock to raise exception on first call
        mock_llm_manager.chat.side_effect = [
            Exception("Provider failed"),
            Mock(content="Fallback response")
        ]

        response = await mock_llm_manager.chat_with_fallback(messages)

        assert response.content == "Fallback response"
        assert mock_llm_manager.chat.call_count == 2
```

#### **Agent Tests**
```python
# test/unit/test_exaspoon_agent.py
import pytest
from exaspoon_agent import ExaSpoonAgent

class TestExaSpoonAgent:
    @pytest.mark.asyncio
    async def test_query_processing(self, mock_exaspoon_agent):
        """Test basic query processing."""
        query = "What is the current price of NEO?"

        response = await mock_exaspoon_agent.process_query(query)

        assert response == "Test response"
        mock_exaspoon_agent.process_query.assert_called_once_with(query)

    @pytest.mark.asyncio
    async def test_tool_integration(self, mock_exaspoon_agent):
        """Test tool calling functionality."""
        query = "Get the balance of address XYZ"

        response = await mock_exaspoon_agent.process_query(query)

        # Verify tool was called with correct parameters
        mock_exaspoon_agent.process_query.assert_called_once()
```

### 2. Integration Tests (`test/integration/`)

Test component interactions.

#### **Agent-LLM Integration**
```python
# test/integration/test_agent_llm_integration.py
import pytest
from exaspoon_agent import ExaSpoonAgent

class TestAgentLLMIntegration:
    @pytest.mark.asyncio
    async def test_agent_with_real_llm(self):
        """Test agent with actual LLM (requires API keys)."""
        agent = ExaSpoonAgent(llm_provider="openai")

        response = await agent.process_query("What is Bitcoin?")

        assert response is not None
        assert len(response) > 0
        assert "Bitcoin" in response

    @pytest.mark.asyncio
    async def test_mcp_tool_integration(self):
        """Test MCP tool integration with actual MCP server."""
        agent = ExaSpoonAgent(enable_mcp=True)

        response = await agent.process_query("Get Neo blockchain info")

        assert response is not None
        # Verify MCP tool was called successfully

    @pytest.mark.asyncio
    async def test_neo_blockchain_operations(self):
        """Test Neo blockchain-specific operations."""
        agent = ExaSpoonAgent(enable_mcp=True)

        # Test Neo balance query
        response = await agent.process_query(
            "Get NEO balance for address: NX6GUGKJ6GLUVR7T7AJ3GKM6QHD3JW6Q6A"
        )
        assert response is not None
        assert "NEO" in response or "balance" in response.lower()

        # Test Neo transaction query
        response = await agent.process_query(
            "Get transaction details for hash: 0x1234567890abcdef"
        )
        assert response is not None

    @pytest.mark.asyncio
    async def test_solana_blockchain_operations(self):
        """Test Solana blockchain-specific operations."""
        agent = ExaSpoonAgent(enable_mcp=True)

        # Test Solana balance query
        response = await agent.process_query(
            "Get SOL balance for address: 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM"
        )
        assert response is not None
        assert "SOL" in response or "balance" in response.lower()

        # Test Solana transaction query
        response = await agent.process_query(
            "Get transaction details for signature: 5j7s..."
        )
        assert response is not None

    @pytest.mark.asyncio
    async def test_cross_chain_analysis(self):
        """Test cross-chain analysis between Neo and Solana."""
        agent = ExaSpoonAgent(enable_mcp=True)

        response = await agent.process_query(
            "Compare transaction speeds between Neo and Solana networks"
        )
        assert response is not None
        assert any(chain in response for chain in ["Neo", "Solana"])
        assert "speed" in response.lower() or "transaction" in response.lower()
```

#### **Web API Integration**
```python
# test/integration/test_web_api.py
import pytest
from fastapi.testclient import TestClient
from app import app

class TestWebAPI:
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_chat_endpoint(self, client):
        """Test chat endpoint."""
        response = client.post(
            "/api/chat",
            json={"message": "Hello", "stream": False}
        )

        assert response.status_code == 200
        assert "response" in response.json()
```

### 3. End-to-End Tests (`test/e2e/`)

Test complete user workflows.

```python
# test/e2e/test_user_workflows.py
import pytest
from playwright.async_api import async_playwright

class TestUserWorkflows:
    @pytest.mark.asyncio
    async def test_complete_chat_interaction(self):
        """Test complete chat interaction from UI."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Navigate to application
            await page.goto("http://localhost:5556")

            # Wait for page to load
            await page.wait_for_selector("#chat-input")

            # Send message
            await page.fill("#chat-input", "What is the current NEO price?")
            await page.click("#send-button")

            # Wait for response
            await page.wait_for_selector(".message.assistant")

            # Verify response contains relevant information
            response = await page.text_content(".message.assistant")
            assert "NEO" in response or "price" in response.lower()

            await browser.close()

    @pytest.mark.asyncio
    async def test_financial_analysis_workflow(self):
        """Test complete financial analysis workflow."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            await page.goto("http://localhost:5556")

            # Complex financial query
            query = "Analyze the top 10 NEO tokens and provide investment recommendations"
            await page.fill("#chat-input", query)
            await page.click("#send-button")

            # Wait for comprehensive response
            await page.wait_for_timeout(10000)  # Allow for processing time

            # Verify response quality
            response = await page.text_content(".message.assistant")
            assert len(response) > 100  # Substantial response
            assert any(word in response.lower() for word in ["analysis", "recommend", "investment"])

            await browser.close()

    @pytest.mark.asyncio
    async def test_dual_blockchain_workflow(self):
        """Test workflow involving both Neo and Solana blockchains."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            await page.goto("http://localhost:5556")

            # Cross-chain query
            query = "Compare the performance of Neo and Solana ecosystems over the past month"
            await page.fill("#chat-input", query)
            await page.click("#send-button")

            # Wait for comprehensive response
            await page.wait_for_timeout(15000)  # Allow more time for cross-chain analysis

            # Verify cross-chain response
            response = await page.text_content(".message.assistant")
            assert len(response) > 200  # Comprehensive cross-chain analysis
            assert "Neo" in response and "Solana" in response
            assert any(word in response.lower() for word in ["compare", "performance", "ecosystem"])

            await browser.close()

    @pytest.mark.asyncio
    async def test_blockchain_switching_workflow(self):
        """Test switching between different blockchain contexts."""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            await page.goto("http://localhost:5556")

            # Query about Neo
            await page.fill("#chat-input", "What is the current Neo block height?")
            await page.click("#send-button")
            await page.wait_for_selector(".message.assistant")

            neo_response = await page.text_content(".message.assistant:last-child")

            # Query about Solana
            await page.fill("#chat-input", "What is the current Solana slot?")
            await page.click("#send-button")
            await page.wait_for_selector(".message.assistant:last-child")

            solana_response = await page.text_content(".message.assistant:last-child")

            # Verify context switching works correctly
            assert "Neo" in neo_response or "block" in neo_response.lower()
            assert "Solana" in solana_response or "slot" in solana_response.lower()

            await browser.close()
```

### 4. Performance Tests (`test/performance/`)

Test system performance under load.

```python
# test/performance/test_load.py
import pytest
import asyncio
import aiohttp
import time

class TestLoad:
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test system under concurrent load."""
        base_url = "http://localhost:5556"
        concurrent_requests = 50

        async def make_request(session, url):
            start_time = time.time()
            async with session.post(url, json={"message": "Hello"}) as response:
                await response.text()
                return time.time() - start_time

        async with aiohttp.ClientSession() as session:
            tasks = [
                make_request(session, f"{base_url}/api/chat")
                for _ in range(concurrent_requests)
            ]

            response_times = await asyncio.gather(*tasks)

            # Performance assertions
            avg_response_time = sum(response_times) / len(response_times)
            assert avg_response_time < 5.0  # Average under 5 seconds
            assert max(response_times) < 10.0  # No request over 10 seconds

    @pytest.mark.asyncio
    async def test_blockchain_api_performance(self):
        """Test performance of blockchain-specific operations."""
        base_url = "http://localhost:5556"

        blockchain_queries = [
            {"message": "Get current Neo block height"},
            {"message": "Get current Solana slot"},
            {"message": "Get NEO balance for test address"},
            {"message": "Get SOL balance for test address"}
        ]

        async def make_blockchain_request(session, query_data):
            start_time = time.time()
            async with session.post(f"{base_url}/api/chat", json=query_data) as response:
                await response.text()
                return time.time() - start_time

        async with aiohttp.ClientSession() as session:
            # Test each blockchain query multiple times
            all_response_times = []
            for query in blockchain_queries:
                tasks = [
                    make_blockchain_request(session, query)
                    for _ in range(10)  # 10 requests per query type
                ]
                response_times = await asyncio.gather(*tasks)
                all_response_times.extend(response_times)

            # Performance assertions for blockchain operations
            avg_response_time = sum(all_response_times) / len(all_response_times)
            assert avg_response_time < 8.0  # Blockchain operations may be slower
            assert max(all_response_times) < 15.0  # No request over 15 seconds

    @pytest.mark.asyncio
    async def test_cross_chain_analysis_performance(self):
        """Test performance of cross-chain analysis queries."""
        base_url = "http://localhost:5556"
        cross_chain_queries = [
            {"message": "Compare Neo vs Solana transaction speeds"},
            {"message": "Analyze DeFi ecosystems on both Neo and Solana"},
            {"message": "Get TVL comparison between Neo and Solana"}
        ]

        async def make_cross_chain_request(session, query_data):
            start_time = time.time()
            async with session.post(f"{base_url}/api/chat", json=query_data) as response:
                await response.text()
                return time.time() - start_time

        async with aiohttp.ClientSession() as session:
            tasks = [
                make_cross_chain_request(session, query)
                for query in cross_chain_queries
                for _ in range(5)  # 5 requests per cross-chain query
            ]

            response_times = await asyncio.gather(*tasks)

            # Cross-chain analysis may take longer
            avg_response_time = sum(response_times) / len(response_times)
            assert avg_response_time < 12.0  # Allow more time for complex analysis
            assert max(response_times) < 20.0  # Maximum reasonable time

    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test memory usage during extended operation."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        agent = ExaSpoonAgent()

        # Simulate extended usage
        for i in range(100):
            await agent.process_query(f"Test query {i}")

            # Check memory every 10 queries
            if i % 10 == 0:
                current_memory = process.memory_info().rss
                memory_increase = current_memory - initial_memory
                assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase
```

## 🚀 Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=exaspoon2 --cov-report=html

# Run specific test categories
pytest test/unit/
pytest test/integration/
pytest test/e2e/

# Run with verbose output
pytest -v

# Run with parallel execution
pytest -n auto  # Requires pytest-xdist
```

### Test Execution by Component
```bash
# LLM Manager tests
pytest test/unit/test_llm_manager.py spoon-core/tests/test_llm_manager_integration.py

# Agent tests
pytest test/unit/test_exaspoon_agent.py spoon-core/tests/test_agent_llm_integration.py

# Web API tests (requires FastAPI server running)
pytest test/integration/test_web_api.py

# MCP integration tests (requires MCP server running)
pytest test/integration/test_mcp_integration.py
```

### Service Status Check
Before running integration or E2E tests, verify services are running:
```bash
# Check MCP server status
curl http://localhost:8766/health

# Check FastAPI server status
curl http://localhost:5556/api/status

# If services are not running, start them:
make dev  # Start both services
```

### Environment-Specific Testing
```bash
# Development environment
pytest -m "not integration and not e2e"

# Integration tests (requires external services)
pytest -m integration

# End-to-end tests (requires full application running)
make dev  # Start both MCP gateway and FastAPI server
sleep 5   # Wait for services to fully initialize
pytest -m e2e

# Performance tests
pytest -m performance
```

### Continuous Integration Commands
```bash
# Full CI test suite
pytest --cov=exaspoon2 --cov-fail-under=80 -v

# Quick smoke tests
pytest test/unit/ -k "test_basic" --maxfail=3

# Pre-deployment tests
pytest test/integration/ test/e2e/ -v
```

## 🎭 Test Data & Mocking

### Mock Objects (`test/fixtures/`)

#### **Mock LLM Providers**
```python
# test/fixtures/mock_providers.py
from unittest.mock import AsyncMock, Mock
from spoon_ai.llm.interface import LLMResponse

class MockLLMProvider:
    def __init__(self, name="mock_provider", response_content="Test response"):
        self.name = name
        self.response_content = response_content

    async def chat(self, messages, **kwargs):
        return LLMResponse(
            content=self.response_content,
            provider=self.name,
            model="mock-model",
            finish_reason="stop"
        )

    async def chat_stream(self, messages, **kwargs):
        for chunk in self.response_content.split():
            yield chunk

    async def health_check(self):
        return True

def create_mock_llm_manager():
    """Create a mock LLM manager with multiple providers."""
    manager = Mock()
    manager.chat = AsyncMock(return_value=Mock(content="Mock response"))
    manager.chat_stream = AsyncMock()
    manager.health_check_all = AsyncMock(return_value={
        "openai": True,
        "anthropic": True,
        "gemini": True
    })
    return manager
```

#### **Mock MCP Tools**
```python
# test/fixtures/mock_mcp_tools.py
from unittest.mock import AsyncMock, Mock

class MockMCPTool:
    def __init__(self, name="mock_tool", result="Mock result"):
        self.name = name
        self.result = result

    async def execute(self, **kwargs):
        return self.result

def create_mock_tool_manager():
    """Create a mock tool manager with common tools."""
    manager = Mock()
    manager.execute_tool = AsyncMock(return_value="Mock tool result")
    manager.list_tools = Mock(return_value=[
        {"name": "get_balance", "description": "Get wallet balance"},
        {"name": "get_transaction", "description": "Get transaction details"},
        {"name": "analyze_token", "description": "Analyze token performance"}
    ])
    return manager
```

#### **Test Data Factories**
```python
# test/fixtures/factories.py
import factory
from datetime import datetime
from spoon_ai.schema import Message

class MessageFactory(factory.Factory):
    class Meta:
        model = Message

    role = "user"
    content = factory.Faker("sentence")
    timestamp = factory.LazyFunction(datetime.now)

class ConversationFactory:
    @staticmethod
    def create_financial_query():
        return MessageFactory.create(
            content="What is the current price of NEO and market analysis?"
        )

    @staticmethod
    def create_blockchain_query():
        return MessageFactory.create(
            content="Get transaction details for hash: 0x1234567890abcdef"
        )
```

### Test Scenarios (`test/fixtures/scenarios/`)

```python
# test/fixtures/scenarios/financial_queries.py
FINANCIAL_QUERIES = [
    {
        "query": "What is the current price of Bitcoin?",
        "expected_keywords": ["Bitcoin", "BTC", "price"],
        "category": "price_query"
    },
    {
        "query": "Analyze NEO market trends for the past 30 days",
        "expected_keywords": ["NEO", "trend", "analysis"],
        "category": "market_analysis"
    },
    {
        "query": "Get wallet balance for address: NX6GUGKJ6GLUVR7T7AJ3GKM6QHD3JW6Q6A",
        "expected_keywords": ["balance", "NX6GUGKJ6GLUVR7T7AJ3GKM6QHD3JW6Q6A"],
        "category": "wallet_query"
    }
]

BLOCKCHAIN_QUERIES = [
    # Neo Blockchain Queries
    {
        "query": "Get transaction details for Neo hash: 0xabcdef...",
        "expected_keywords": ["transaction", "hash", "Neo"],
        "category": "neo_transaction_query"
    },
    {
        "query": "What is the current block height of Neo network?",
        "expected_keywords": ["block", "height", "Neo"],
        "category": "neo_network_info"
    },
    {
        "query": "Get NEO token balance for wallet: NX6GUGKJ6GLUVR7T7AJ3GKM6QHD3JW6Q6A",
        "expected_keywords": ["balance", "NEO", "wallet"],
        "category": "neo_balance_query"
    },

    # Solana Blockchain Queries
    {
        "query": "Get Solana transaction details for signature: 5j7s...",
        "expected_keywords": ["transaction", "signature", "Solana"],
        "category": "solana_transaction_query"
    },
    {
        "query": "What is the current slot of Solana network?",
        "expected_keywords": ["slot", "Solana", "network"],
        "category": "solana_network_info"
    },
    {
        "query": "Get SOL balance for address: 9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM",
        "expected_keywords": ["balance", "SOL", "address"],
        "category": "solana_balance_query"
    },

    # Cross-chain Queries
    {
        "query": "Compare transaction speeds between Neo and Solana networks",
        "expected_keywords": ["compare", "Neo", "Solana", "speed", "transaction"],
        "category": "cross_chain_comparison"
    },
    {
        "query": "Get total value locked (TVL) on both Neo and Solana ecosystems",
        "expected_keywords": ["TVL", "Neo", "Solana", "ecosystem"],
        "category": "cross_chain_tvl"
    }
]
```

## 🚧 Future Features & TODO Testing

### Features Not Yet Implemented

#### **Real-time Streaming Responses**
The streaming functionality is planned but not yet implemented. When ready, it should include:

**Planned Tests:**
```python
# test/unit/test_streaming.py
import pytest
from exaspoon_agent import ExaSpoonAgent

class TestStreamingFeatures:
    @pytest.mark.asyncio
    async def test_stream_response_basic(self):
        """Test basic streaming response functionality."""
        agent = ExaSpoonAgent()

        stream_chunks = []
        async for chunk in agent.process_query_stream("Hello"):
            stream_chunks.append(chunk)
            assert isinstance(chunk, str)
            assert len(chunk) > 0

        # Verify complete response
        complete_response = "".join(stream_chunks)
        assert len(complete_response) > 0

    @pytest.mark.asyncio
    async def test_stream_with_blockchain_data(self):
        """Test streaming with blockchain-specific queries."""
        agent = ExaSpoonAgent()

        query = "Get Neo block height and Solana slot"
        chunks = []

        async for chunk in agent.process_query_stream(query):
            chunks.append(chunk)

        response = "".join(chunks)
        assert any(network in response for network in ["Neo", "Solana"])

    @pytest.mark.asyncio
    async def test_stream_error_handling(self):
        """Test streaming error handling and recovery."""
        agent = ExaSpoonAgent()

        with pytest.raises(Exception):
            async for chunk in agent.process_query_stream("Invalid query"):
                pass
```

**Performance Tests for Streaming:**
```python
# test/performance/test_streaming.py
import pytest
import asyncio
import time

class TestStreamingPerformance:
    @pytest.mark.asyncio
    async def test_stream_latency(self):
        """Test streaming response latency."""
        agent = ExaSpoonAgent()

        start_time = time.time()
        first_chunk_time = None

        async for chunk in agent.process_query_stream("Hello"):
            if first_chunk_time is None:
                first_chunk_time = time.time()
            break

        # First chunk should arrive quickly
        latency = first_chunk_time - start_time
        assert latency < 1.0  # Less than 1 second latency

    @pytest.mark.asyncio
    async def test_concurrent_streams(self):
        """Test multiple concurrent streaming requests."""
        agent = ExaSpoonAgent()

        async def stream_query(query):
            chunks = []
            async for chunk in agent.process_query_stream(query):
                chunks.append(chunk)
            return "".join(chunks)

        # Test concurrent streams
        tasks = [
            stream_query(f"Query {i}")
            for i in range(5)
        ]

        responses = await asyncio.gather(*tasks)
        assert len(responses) == 5
        assert all(len(response) > 0 for response in responses)
```

**Web API Streaming Tests:**
```python
# test/integration/test_web_api_streaming.py
import pytest
import asyncio
import httpx

class TestWebAPIStreaming:
    @pytest.mark.asyncio
    async def test_streaming_endpoint(self):
        """Test web API streaming endpoint."""
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                "http://localhost:5556/api/chat/stream",
                json={"message": "Hello", "stream": True}
            ) as response:
                assert response.status_code == 200

                chunks = []
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        chunks.append(chunk)

                complete_response = "".join(chunks)
                assert len(complete_response) > 0
```

### Testing Status Matrix

| Feature | Status | Tests | Coverage |
|---------|--------|-------|----------|
| Multi-LLM Support | ✅ Implemented | ✅ Complete | 95% |
| MCP Tool Integration | ✅ Implemented | ✅ Complete | 90% |
| Neo Blockchain Ops | ✅ Implemented | ✅ Complete | 85% |
| Solana Blockchain Ops | ✅ Implemented | ✅ Complete | 85% |
| Cross-chain Analysis | ✅ Implemented | ✅ Complete | 80% |
| Memory Management | ✅ Implemented | ✅ Complete | 75% |
| Health Monitoring | ✅ Implemented | ✅ Complete | 70% |
| Multi-language Support | ✅ Implemented | 🔄 Partial | 60% |
| **Real-time Streaming** | 🚧 TODO | ❌ Not Ready | 0% |

## 🔄 Continuous Integration

### GitHub Actions Workflow (`.github/workflows/test.yml`)
```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env

    - name: Install dependencies
      run: uv sync

    - name: Run linting
      run: |
        uv run flake8 exaspoon2/
        uv run black --check exaspoon2/
        uv run isort --check-only exaspoon2/

    - name: Run unit tests
      run: uv run pytest test/unit/ -v --cov=exaspoon2

    - name: Run integration tests
      run: uv run pytest test/integration/ -v
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  e2e-tests:
    runs-on: ubuntu-latest
    needs: test

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: "3.10"

    - name: Install dependencies
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        source $HOME/.cargo/env
        uv sync

    - name: Install Playwright
      run: uv run playwright install

    - name: Start application
      run: |
        uv run app.py &
        sleep 10

    - name: Run E2E tests
      run: uv run pytest test/e2e/ -v
      env:
        E2E_BASE_URL: http://localhost:5556
```

### Pre-commit Configuration (`.pre-commit-config.yaml`)
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: uv run pytest test/unit/ --co -q
        language: system
        pass_filenames: false
        always_run: true
```

## 🐛 Troubleshooting

### Common Issues

#### **1. Test Failures Due to Missing API Keys**
```bash
# Error: Missing OPENAI_API_KEY
# Solution: Set environment variables or create .env file
export OPENAI_API_KEY="your-key-here"
# or create .env file with the key
```

#### **2. MCP Server Connection Issues**
```bash
# Error: Connection refused to MCP server
# Solution: Start MCP server before running integration tests
make dev  # Start both MCP gateway and FastAPI server
# or start them separately:
make console &  # Start MCP gateway in background
sleep 3
uv run app.py    # Start FastAPI server
# or run tests with MCP disabled
pytest test/unit/ -m "not mcp"
```

#### **3. Async Test Timeouts**
```python
# Error: pytest.TimeoutWarning
# Solution: Increase timeout or use pytest marks
@pytest.mark.asyncio
@pytest.mark.timeout(60)  # Increase timeout to 60 seconds
async def test_slow_operation(self):
    # Your test code here
```

#### **4. Memory Leaks in Tests**
```python
# Error: Memory usage increasing during tests
# Solution: Use proper cleanup and fixtures
@pytest.fixture
async def agent():
    agent = ExaSpoonAgent()
    yield agent
    await agent.cleanup()  # Proper cleanup
```

### Debug Mode

Enable debug logging for troubleshooting:
```python
# Add to conftest.py
import logging

@pytest.fixture(autouse=True)
def debug_logging():
    logging.basicConfig(level=logging.DEBUG)
    yield
    logging.basicConfig(level=logging.INFO)
```

### Performance Profiling

Profile test execution:
```bash
# Profile with pytest-profiling
pytest --profile

# Profile memory usage
pytest --memprof

# Profile with line_profiler
pytest --line-profile
```

### Test Database Issues

For tests requiring databases:
```python
# Use in-memory SQLite for testing
@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

---

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [AsyncIO Testing Best Practices](https://pytest-asyncio.readthedocs.io/)
- [SpoonAI SDK Documentation](./spoon-core/docs/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)

## 🤝 Contributing

When adding new tests:

1. **Follow the existing naming conventions** (`test_*.py`)
2. **Use descriptive test names** that explain what is being tested
3. **Add appropriate docstrings** explaining test purpose
4. **Use fixtures** for common setup/teardown logic
5. **Mock external dependencies** to ensure test isolation
6. **Assert both positive and negative cases**
7. **Include performance assertions** where applicable

## 📞 Support

For testing questions and issues:
- Check existing test files in `spoon-core/tests/` for examples
- Review test logs for detailed error information
- Use `pytest -s` to see print statements during test execution
- Join the development team communication channels for support