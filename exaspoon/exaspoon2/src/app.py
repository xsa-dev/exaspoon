#!/usr/bin/env python3
"""FastAPI server for the ExaspoonAi chat interface."""

import json
import logging
import os

# Load environment variables from .env file
import pathlib
import secrets
import signal
import sys
import time
from contextlib import asynccontextmanager
from typing import Dict

from dotenv import load_dotenv
from fastapi import (
    Body,
    FastAPI,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

project_root = pathlib.Path(__file__).parent.parent
load_dotenv(project_root / ".env")

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
# Add spoon-core to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "spoon-core"))

from chart_service import chart_service
from exaspoon_agent import ExaSpoonAgent
from realtime_service import realtime_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionManager:
    """Manages multiple ExaSpoonAgent instances for different sessions."""

    def __init__(self):
        self.agents: Dict[str, ExaSpoonAgent] = {}
        self.agent_status: Dict[str, bool] = {}

    def get_or_create_agent(self, session_id: str) -> ExaSpoonAgent:
        """Get existing agent or create new one for session."""
        if session_id not in self.agents:
            logger.info(f"🆕 Creating new agent for session {session_id}")
            self.agents[session_id] = ExaSpoonAgent()
            self.agent_status[session_id] = False

        return self.agents[session_id]

    async def initialize_agent(self, session_id: str) -> bool:
        """Initialize agent for specific session."""
        agent = self.get_or_create_agent(session_id)

        if not self.agent_status.get(session_id, False):
            try:
                logger.info(f"🔄 Initializing agent for session {session_id}")
                initialized = await agent.initialize()
                self.agent_status[session_id] = bool(initialized)

                if self.agent_status[session_id]:
                    logger.info(f"✅ Agent initialized for session {session_id}")
                else:
                    logger.warning(
                        f"⚠️ Agent initialization failed for session {session_id}"
                    )

                return self.agent_status[session_id]
            except Exception as exc:
                logger.error(
                    f"❌ Agent initialization error for session {session_id}: {exc}"
                )
                self.agent_status[session_id] = False
                return False

        return self.agent_status[session_id]

    async def cleanup_agent(self, session_id: str):
        """Cleanup agent for specific session."""
        if session_id in self.agents:
            try:
                await self.agents[session_id].cleanup()
                logger.info(f"🧹 Cleaned up agent for session {session_id}")
            except Exception as exc:
                logger.warning(
                    f"⚠️ Agent cleanup warning for session {session_id}: {exc}"
                )
            finally:
                del self.agents[session_id]
                if session_id in self.agent_status:
                    del self.agent_status[session_id]

    def get_agent_status(self, session_id: str) -> bool:
        """Get initialization status for agent."""
        return self.agent_status.get(session_id, False)

    def get_all_sessions(self) -> list:
        """Get list of all active session IDs."""
        return list(self.agents.keys())


# Global session manager
session_manager = SessionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the application when it starts."""
    # Startup logic
    # MCP server is started by the Makefile, no need to start it here
    # Agents will be initialized per session when needed

    # Start realtime subscriptions
    await realtime_service.start_subscriptions()
    logger.info(
        "🚀 ExaspoonAi FastAPI application started with session support and real-time features"
    )

    # Yield control to the application
    yield

    # Shutdown logic - cleanup all session agents
    logger.info("🛑 Shutting down application and cleaning up all sessions...")
    active_sessions = session_manager.get_all_sessions()
    for session_id in active_sessions:
        await session_manager.cleanup_agent(session_id)

    # Cleanup realtime service
    await realtime_service.cleanup()
    logger.info("✅ All session agents and realtime service cleaned up")


app = FastAPI(title="ExaspoonAi Chat Interface", lifespan=lifespan)

# Add session middleware with a secret key
app.add_middleware(
    SessionMiddleware, secret_key="prometheus-ai-session-secret-key-2024"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"🛑 Received signal {signum}, shutting down...")
    sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def get_session_id(request: Request) -> str:
    """Get or create session ID from request."""
    if "session_id" not in request.session:
        request.session["session_id"] = secrets.token_urlsafe(32)
        logger.info(f"🆕 Created new session: {request.session['session_id']}")
    return request.session["session_id"]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main HTML page with session ID."""
    try:
        session_id = get_session_id(request)

        with open("templates/page.html", "r", encoding="utf-8") as f:
            html_content = f.read()

        # Inject session ID into HTML
        html_content = html_content.replace(
            "<!-- Session ID will be injected here -->",
            f'<script>window.sessionId = "{session_id}";</script>',
        )

        return html_content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="HTML file not found")
    except Exception as exc:
        logger.error(f"Error serving page: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/chat")
async def chat(request: ChatRequest = Body(...), http_request: Request = None):
    """Process user input through the session-specific MCP agent."""
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Empty message")

    # Get session ID
    session_id = get_session_id(http_request)
    logger.info(f"💬 Chat request from session {session_id}")

    # Get or create agent for this session
    try:
        # Initialize agent if not already initialized
        is_initialized = await session_manager.initialize_agent(session_id)
        if not is_initialized:
            # Return error message but don't crash
            logger.warning(f"⚠️ Agent not initialized for session {session_id}")
            return {
                "response": "❌ Agent is currently initializing. Please try again in a moment.",
                "timestamp": time.time(),
                "session_id": session_id,
            }

        agent = session_manager.get_or_create_agent(session_id)

        # Query the agent
        response = await agent.query_agent(message)
        return {
            "response": response,
            "timestamp": time.time(),
            "session_id": session_id,
        }
    except Exception as exc:
        logger.error(f"❌ Chat endpoint error for session {session_id}: {exc}")
        return {
            "response": f"❌ Error processing request: {str(exc)}",
            "timestamp": time.time(),
            "session_id": session_id,
        }


@app.get("/api/status")
async def status(http_request: Request):
    """Check the status of the session-specific agent and MCP server."""
    session_id = get_session_id(http_request)

    # Get session-specific agent
    agent = session_manager.agents.get(session_id)
    agent_initialized = session_manager.get_agent_status(session_id)

    if agent and hasattr(agent, "get_status"):
        # Use the enhanced status method from agent
        try:
            agent_status = await agent.get_status()
            agent_status["session_id"] = session_id
            agent_status["agent_initialized"] = agent_initialized
            agent_status["active_sessions"] = len(session_manager.get_all_sessions())
            return agent_status
        except Exception as e:
            logger.error(f"❌ Failed to get agent status for session {session_id}: {e}")
            # Fallback to basic status
            pass

    # Check if MCP server is running by checking if the port is accessible
    try:
        import httpx

        mcp_gateway_host = os.getenv("MCP_GATEWAY_HOST", "localhost")
        mcp_gateway_port = os.getenv("MCP_GATEWAY_PORT", "8766")

        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(
                f"http://{mcp_gateway_host}:{mcp_gateway_port}/"
            )
            mcp_server_running = response.status_code < 500
    except Exception:
        mcp_server_running = False

    return {
        "session_id": session_id,
        "agent_initialized": agent_initialized,
        "fallback_mode": False,
        "llm_manager_available": False,
        "mcp_server_running": mcp_server_running,
        "mcp_server_healthy": mcp_server_running,
        "available_tools": 0,
        "active_sessions": len(session_manager.get_all_sessions()),
        "mcp_server_url": f"http://{mcp_gateway_host}:{mcp_gateway_port}/mcp",
        "timestamp": time.time(),
    }


@app.get("/api/agent/tools")
async def get_available_tools(http_request: Request):
    """Get list of available MCP tools for the session."""
    try:
        session_id = get_session_id(http_request)
        agent = session_manager.agents.get(session_id)

        # Use enhanced status method if available
        if agent and hasattr(agent, "get_status"):
            try:
                status = await agent.get_status()
                if status["available_tools"] > 0:
                    # Try to get detailed tool info
                    tools = []
                    if (
                        hasattr(agent, "agent")
                        and hasattr(agent.agent, "tools")
                        and hasattr(agent.agent.tools, "tools")
                    ):
                        for tool in agent.agent.tools.tools:
                            if hasattr(tool, "name") and hasattr(tool, "description"):
                                tool_info = {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "type": type(tool).__name__,
                                }
                                # Add parameters info if available
                                if hasattr(tool, "parameters") and tool.parameters:
                                    tool_info["parameters"] = tool.parameters
                                tools.append(tool_info)

                    return {
                        "session_id": session_id,
                        "tools": tools,
                        "count": len(tools),
                        "agent_mode": "Full"
                        if not status.get("fallback_mode", False)
                        else "Fallback",
                        "mcp_server_healthy": status.get("mcp_server_healthy", False),
                    }
            except Exception as status_e:
                logger.warning(
                    f"⚠️ Could not get enhanced status for session {session_id}: {status_e}"
                )

        # Fallback tool detection
        if not agent or not hasattr(agent, "agent"):
            return {
                "session_id": session_id,
                "tools": [],
                "error": "Agent not initialized",
                "count": 0,
            }

        tools = []
        if hasattr(agent.agent, "tools") and hasattr(agent.agent.tools, "tools"):
            for tool in agent.agent.tools.tools:
                if hasattr(tool, "name") and hasattr(tool, "description"):
                    tools.append(
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "type": type(tool).__name__,
                        }
                    )

        return {"session_id": session_id, "tools": tools, "count": len(tools)}

    except Exception as exc:
        logger.error(f"❌ Failed to get tools: {exc}")
        return {"tools": [], "error": str(exc), "count": 0}


@app.post("/api/agent/reinitialize")
async def reinitialize_agent(http_request: Request):
    """Reinitialize the session-specific agent with enhanced status reporting."""
    try:
        session_id = get_session_id(http_request)
        logger.info(f"🔄 Reinitializing agent for session {session_id}")

        # Cleanup existing agent for this session
        await session_manager.cleanup_agent(session_id)

        # Create and initialize new agent for this session
        initialized = await session_manager.initialize_agent(session_id)

        if initialized:
            logger.info(f"✅ Agent reinitialized successfully for session {session_id}")

            # Get detailed status
            try:
                agent = session_manager.get_or_create_agent(session_id)
                status = await agent.get_status()
                return {
                    "session_id": session_id,
                    "success": True,
                    "message": "Agent reinitialized successfully",
                    "status": status,
                }
            except Exception as status_e:
                logger.warning(
                    f"⚠️ Could not get detailed status for session {session_id}: {status_e}"
                )
                return {
                    "session_id": session_id,
                    "success": True,
                    "message": "Agent reinitialized successfully",
                    "agent_initialized": True,
                    "fallback_mode": False,
                }
        else:
            logger.warning(
                f"⚠️ Agent initialization returned False for session {session_id}"
            )
            return {
                "session_id": session_id,
                "success": False,
                "message": "Failed to reinitialize agent - initialization returned False",
                "agent_initialized": False,
                "fallback_mode": True,
            }

    except Exception as exc:
        logger.error(f"❌ Agent reinitialization failed: {exc}")
        return {
            "success": False,
            "message": f"Reinitialization failed: {str(exc)}",
            "agent_initialized": False,
            "error": str(exc),
        }


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest = Body(...), http_request: Request = None):
    """Process user input through the session-specific MCP agent with streaming response."""
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Empty message")

    # Get session ID
    session_id = get_session_id(http_request)
    logger.info(f"💬 Streaming chat request from session {session_id}")

    # Check if agent is initialized
    is_initialized = await session_manager.initialize_agent(session_id)
    if not is_initialized:
        error_msg = "Agent is currently initializing. Please try again in a moment."
        logger.warning(f"⚠️ Agent not initialized for streaming session {session_id}")

        async def error_response():
            yield f"data: {json.dumps({'error': error_msg, 'session_id': session_id})}\n\n"

        return StreamingResponse(error_response(), media_type="text/plain")

    agent = session_manager.get_or_create_agent(session_id)

    async def generate_response():
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Processing your request...', 'session_id': session_id})}\n\n"

            # Get response from agent
            response = await agent.query_agent(message)

            # Send the response
            yield f"data: {json.dumps({'type': 'response', 'content': response, 'session_id': session_id})}\n\n"

            # Send completion status
            yield f"data: {json.dumps({'type': 'done', 'session_id': session_id})}\n\n"

        except Exception as exc:
            logger.error(f"❌ Streaming chat error for session {session_id}: {exc}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc), 'session_id': session_id})}\n\n"

    return StreamingResponse(generate_response(), media_type="text/plain")


@app.get("/api/sessions")
async def get_sessions():
    """Get information about active sessions."""
    try:
        active_sessions = session_manager.get_all_sessions()
        session_info = []

        for session_id in active_sessions:
            agent = session_manager.agents.get(session_id)
            is_initialized = session_manager.get_agent_status(session_id)

            session_data = {
                "session_id": session_id,
                "initialized": is_initialized,
                "created_at": None,  # Could add timestamp tracking in SessionManager
            }

            # Try to get additional agent info
            if agent and hasattr(agent, "get_status"):
                try:
                    status = await agent.get_status()
                    session_data.update(
                        {
                            "available_tools": status.get("available_tools", 0),
                            "fallback_mode": status.get("fallback_mode", False),
                            "mcp_server_healthy": status.get(
                                "mcp_server_healthy", False
                            ),
                        }
                    )
                except Exception:
                    pass

            session_info.append(session_data)

        return {
            "active_sessions": len(active_sessions),
            "sessions": session_info,
            "timestamp": time.time(),
        }
    except Exception as exc:
        logger.error(f"❌ Failed to get sessions info: {exc}")
        return {
            "active_sessions": 0,
            "sessions": [],
            "error": str(exc),
            "timestamp": time.time(),
        }


@app.websocket("/ws/realtime/{session_id}")
async def websocket_realtime(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time data updates."""
    await websocket.accept()
    logger.info(f"🔌 WebSocket connection established for session {session_id}")

    # Register the WebSocket connection
    realtime_service.register_websocket(session_id, websocket)

    try:
        # Send initial connection status
        await websocket.send_text(
            json.dumps(
                {
                    "type": "connection_status",
                    "status": "connected",
                    "session_id": session_id,
                    "timestamp": time.time(),
                }
            )
        )

        # Keep the connection alive and listen for client messages
        while True:
            try:
                # Wait for client message
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle client requests
                await _handle_websocket_message(websocket, session_id, message)

            except WebSocketDisconnect:
                logger.info(f"🔌 WebSocket disconnected for session {session_id}")
                break
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Invalid JSON received from session {session_id}")
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": "Invalid JSON format",
                            "session_id": session_id,
                        }
                    )
                )
            except Exception as e:
                logger.error(f"❌ WebSocket error for session {session_id}: {e}")
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "error",
                            "message": f"WebSocket error: {str(e)}",
                            "session_id": session_id,
                        }
                    )
                )

    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"❌ WebSocket connection error for session {session_id}: {e}")
    finally:
        # Unregister the WebSocket connection
        await realtime_service.unregister_websocket(session_id)


async def _handle_websocket_message(
    websocket: WebSocket, session_id: str, message: dict
):
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")

    if message_type == "ping":
        # Respond to ping with pong
        await websocket.send_text(
            json.dumps(
                {"type": "pong", "session_id": session_id, "timestamp": time.time()}
            )
        )

    elif message_type == "refresh_data":
        # Trigger data refresh
        data_type = message.get("data_type", "all")
        await realtime_service.trigger_data_refresh(data_type)

    elif message_type == "get_status":
        # Send connection status
        status = realtime_service.get_connection_status()
        await websocket.send_text(
            json.dumps(
                {"type": "status_response", "status": status, "session_id": session_id}
            )
        )

    else:
        logger.warning(
            f"⚠️ Unknown message type: {message_type} from session {session_id}"
        )


@app.get("/api/realtime/status")
async def get_realtime_status():
    """Get real-time service status."""
    try:
        status = realtime_service.get_connection_status()
        return {
            "status": status,
            "timestamp": time.time(),
        }
    except Exception as exc:
        logger.error(f"Failed to get realtime status: {exc}")
        return {"error": str(exc), "timestamp": time.time()}


@app.post("/api/realtime/refresh")
async def trigger_realtime_refresh(data_type: str = "all"):
    """Trigger a manual data refresh for all connected clients."""
    try:
        await realtime_service.trigger_data_refresh(data_type)
        return {
            "message": f"Data refresh triggered for type: {data_type}",
            "timestamp": time.time(),
        }
    except Exception as exc:
        logger.error(f"Failed to trigger refresh: {exc}")
        return {"error": str(exc), "timestamp": time.time()}


@app.get("/api/chart/monthly-totals")
async def get_monthly_totals(months: int = 12):
    """Get monthly totals for chart display."""
    try:
        if months < 1 or months > 24:
            raise HTTPException(
                status_code=400, detail="Months must be between 1 and 24"
            )

        data = await chart_service.get_monthly_totals(months)
        return {"data": data, "timestamp": time.time()}
    except Exception as exc:
        logger.error(f"Failed to get monthly totals: {exc}")
        raise HTTPException(status_code=500, detail="Failed to fetch chart data")


@app.get("/api/chart/category-breakdown")
async def get_category_breakdown(months: int = 1):
    """Get category breakdown for recent transactions."""
    try:
        if months < 1 or months > 12:
            raise HTTPException(
                status_code=400, detail="Months must be between 1 and 12"
            )

        data = await chart_service.get_category_breakdown(months)
        return {"data": data, "timestamp": time.time()}
    except Exception as exc:
        logger.error(f"Failed to get category breakdown: {exc}")
        raise HTTPException(status_code=500, detail="Failed to fetch category data")


@app.get("/api/chart/accounts")
async def get_account_summary():
    """Get account summary."""
    try:
        data = await chart_service.get_account_summary()
        return {"data": data, "timestamp": time.time()}
    except Exception as exc:
        logger.error(f"Failed to get account summary: {exc}")
        raise HTTPException(status_code=500, detail="Failed to fetch account data")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(status_code=404, content={"error": "Endpoint not found"})
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"❌ Internal server error: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


if __name__ == "__main__":
    import uvicorn

    logger.info("🚀 Starting ExaspoonAi FastAPI server...")
    fastapi_host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    fastapi_port = int(os.getenv("FASTAPI_PORT", "5556"))
    uvicorn.run("app:app", host=fastapi_host, port=fastapi_port, reload=False)
