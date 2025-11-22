#!/usr/bin/env python3
"""Simplified FastAPI server for testing session functionality."""

import asyncio
import logging
import os
import secrets
import time
from typing import Dict
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionManager:
    """Manages multiple mock agent instances for different sessions."""

    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.agent_status: Dict[str, bool] = {}

    def get_or_create_agent(self, session_id: str) -> Dict:
        """Get existing agent or create new one for session."""
        if session_id not in self.agents:
            logger.info(f"🆕 Creating new agent for session {session_id}")
            self.agents[session_id] = {
                "session_id": session_id,
                "created_at": time.time(),
                "messages": []
            }
            self.agent_status[session_id] = False

        return self.agents[session_id]

    async def initialize_agent(self, session_id: str) -> bool:
        """Initialize agent for specific session."""
        agent = self.get_or_create_agent(session_id)

        if not self.agent_status.get(session_id, False):
            # Simulate initialization delay
            await asyncio.sleep(0.1)
            self.agent_status[session_id] = True
            logger.info(f"✅ Agent initialized for session {session_id}")

        return self.agent_status[session_id]

    async def cleanup_agent(self, session_id: str):
        """Cleanup agent for specific session."""
        if session_id in self.agents:
            logger.info(f"🧹 Cleaned up agent for session {session_id}")
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
    logger.info("🚀 Test FastAPI application started with session support")
    yield
    logger.info("🛑 Shutting down application...")


app = FastAPI(title="Session Test Interface", lifespan=lifespan)

# Add session middleware with a secret key
app.add_middleware(SessionMiddleware, secret_key="test-session-secret-key-2024")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str


def get_session_id(request: Request) -> str:
    """Get or create session ID from request."""
    if "session_id" not in request.session:
        request.session["session_id"] = secrets.token_urlsafe(16)
        logger.info(f"🆕 Created new session: {request.session['session_id']}")
    return request.session["session_id"]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve a simple HTML page with session info."""
    try:
        session_id = get_session_id(request)

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Session Test</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .session-info {{ background: #f0f0f0; padding: 20px; border-radius: 8px; }}
                .chat-box {{ border: 1px solid #ccc; height: 300px; overflow-y: auto; padding: 10px; margin: 20px 0; }}
                .input-box {{ width: 300px; padding: 10px; }}
                .send-btn {{ padding: 10px 20px; }}
            </style>
        </head>
        <body>
            <h1>Multi-Session Test Interface</h1>

            <div class="session-info">
                <h3>Session Information</h3>
                <p><strong>Session ID:</strong> {session_id}</p>
                <p><strong>Time:</strong> {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <button onclick="checkStatus()">Check Status</button>
                <button onclick="checkSessions()">View All Sessions</button>
            </div>

            <div class="chat-box" id="chatBox">
                <div><em>Messages will appear here...</em></div>
            </div>

            <div>
                <input type="text" id="messageInput" class="input-box" placeholder="Type a message...">
                <button onclick="sendMessage()" class="send-btn">Send</button>
            </div>

            <script>
                window.sessionId = "{session_id}";
                console.log('🔗 Session ID:', window.sessionId);

                async function sendMessage() {{
                    const input = document.getElementById('messageInput');
                    const message = input.value.trim();
                    if (!message) return;

                    const chatBox = document.getElementById('chatBox');
                    chatBox.innerHTML += '<div><strong>You:</strong> ' + message + '</div>';

                    try {{
                        const response = await fetch('/api/chat', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ message }})
                        }});
                        const result = await response.json();
                        chatBox.innerHTML += '<div><strong>Bot:</strong> ' + result.response + '</div>';
                        chatBox.scrollTop = chatBox.scrollHeight;
                    }} catch (error) {{
                        chatBox.innerHTML += '<div><strong>Error:</strong> ' + error.message + '</div>';
                    }}

                    input.value = '';
                }}

                async function checkStatus() {{
                    try {{
                        const response = await fetch('/api/status');
                        const status = await response.json();
                        alert('Session Status:\\n' + JSON.stringify(status, null, 2));
                    }} catch (error) {{
                        alert('Error: ' + error.message);
                    }}
                }}

                async function checkSessions() {{
                    try {{
                        const response = await fetch('/api/sessions');
                        const sessions = await response.json();
                        alert('All Sessions:\\n' + JSON.stringify(sessions, null, 2));
                    }} catch (error) {{
                        alert('Error: ' + error.message);
                    }}
                }}

                document.getElementById('messageInput').addEventListener('keypress', function(e) {{
                    if (e.key === 'Enter') {{
                        sendMessage();
                    }}
                }});
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    except Exception as exc:
        logger.error(f"Error serving page: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/chat")
async def chat(request: ChatRequest = Body(...), http_request: Request = None):
    """Process user input through the session-specific mock agent."""
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Empty message")

    # Get session ID
    session_id = get_session_id(http_request)
    logger.info(f"💬 Chat request from session {session_id}: {message}")

    # Get or create agent for this session
    try:
        # Initialize agent if not already initialized
        is_initialized = await session_manager.initialize_agent(session_id)
        agent = session_manager.get_or_create_agent(session_id)

        # Store message
        agent["messages"].append({
            "content": message,
            "type": "user",
            "timestamp": time.time()
        })

        # Generate mock response
        response = f"Hello from session {session_id}! You said: '{message}'"

        # Store response
        agent["messages"].append({
            "content": response,
            "type": "assistant",
            "timestamp": time.time()
        })

        return {
            "response": response,
            "timestamp": time.time(),
            "session_id": session_id
        }
    except Exception as exc:
        logger.error(f"❌ Chat endpoint error for session {session_id}: {exc}")
        return {
            "response": f"❌ Error processing request: {str(exc)}",
            "timestamp": time.time(),
            "session_id": session_id
        }


@app.get("/api/status")
async def status(http_request: Request):
    """Check the status of the session-specific agent."""
    session_id = get_session_id(http_request)
    agent = session_manager.agents.get(session_id)
    agent_initialized = session_manager.get_agent_status(session_id)

    return {
        "session_id": session_id,
        "agent_initialized": agent_initialized,
        "active_sessions": len(session_manager.get_all_sessions()),
        "message_count": len(agent["messages"]) if agent else 0,
        "timestamp": time.time(),
    }


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
                "message_count": len(agent["messages"]) if agent else 0,
                "created_at": agent.get("created_at") if agent else None
            }
            session_info.append(session_data)

        return {
            "active_sessions": len(active_sessions),
            "sessions": session_info,
            "timestamp": time.time()
        }
    except Exception as exc:
        logger.error(f"❌ Failed to get sessions info: {exc}")
        return {
            "active_sessions": 0,
            "sessions": [],
            "error": str(exc),
            "timestamp": time.time()
        }


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting test session server...")
    uvicorn.run("test_sessions:app", host="0.0.0.0", port=5557, reload=False)