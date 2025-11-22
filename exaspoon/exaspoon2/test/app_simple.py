#!/usr/bin/env python3
"""Simplified FastAPI server for testing chart functionality."""

import logging
import time
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel

from chart_service import chart_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ExaspoonAi Chart Interface")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatRequest(BaseModel):
    message: str


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main HTML page."""
    try:
        with open("templates/page.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="HTML file not found")
    except Exception as exc:
        logger.error(f"Error serving page: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/chat")
async def chat(request: ChatRequest = Body(...)):
    """Simple chat endpoint for testing."""
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Empty message")

    # Simple echo response for testing
    response = f"You said: {message}. This is a test response."
    return {"response": response, "timestamp": time.time()}


@app.get("/api/status")
async def status():
    """Check the status of the application."""
    return {
        "agent_initialized": True,  # Simplified - always true for testing
        "timestamp": time.time(),
    }


@app.get("/api/chart/monthly-totals")
async def get_monthly_totals(months: int = 12):
    """Get monthly totals for chart display."""
    try:
        if months < 1 or months > 24:
            raise HTTPException(status_code=400, detail="Months must be between 1 and 24")

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
            raise HTTPException(status_code=400, detail="Months must be between 1 and 12")

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

    logger.info("🚀 Starting ExaspoonAi Chart FastAPI server...")
    uvicorn.run("app_simple:app", host="0.0.0.0", port=5555, reload=False)