#!/usr/bin/env python3
"""Real-time service for Supabase subscriptions and WebSocket broadcasting."""

import asyncio
import json
import logging
import os
import pathlib
from datetime import datetime
from typing import Any, Dict, List, Set

from dotenv import load_dotenv

project_root = pathlib.Path(__file__).parent.parent
load_dotenv(project_root / ".env")

try:
    # Import async client for realtime features

    from supabase import AsyncClient, Client, create_async_client, create_client
except ImportError:
    logging.warning("Supabase client not available. Real-time features disabled.")
    Client = None
    AsyncClient = None

logger = logging.getLogger(__name__)


class RealtimeService:
    """Service for managing Supabase real-time subscriptions and WebSocket connections."""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", self.supabase_key)

        # WebSocket connections management
        self.websockets: Dict[str, Any] = {}  # session_id -> websocket
        self.active_sessions: Set[str] = set()

        # Supabase clients
        self.supabase_client: Client = None  # Sync client for general operations
        self.supabase_async_client: AsyncClient = None  # Async client for realtime
        self.subscriptions = {}

        # Event queues for broadcasting
        self.event_queues = {}

        self._initialize_supabase()

    def _initialize_supabase(self):
        """Initialize Supabase clients for real-time subscriptions."""
        if not all([self.supabase_url, self.supabase_anon_key]) or Client is None:
            logger.warning(
                "Supabase credentials or client not available. Real-time features disabled."
            )
            return

        try:
            # Initialize sync client for general operations
            self.supabase_client = create_client(
                supabase_url=self.supabase_url, supabase_key=self.supabase_key
            )

            # Note: Async client will be initialized in start_subscriptions method
            # because create_async_client needs to be awaited
            self.supabase_async_client = None
            if AsyncClient is not None:
                logger.info(
                    "✅ Async client import successful, will initialize async client in start_subscriptions"
                )
            else:
                logger.warning(
                    "⚠️ Async client not available, realtime features disabled"
                )

        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase clients: {e}")

    async def start_subscriptions(self):
        """Start all real-time subscriptions."""
        # Initialize async client first
        if AsyncClient is not None and self.supabase_async_client is None:
            try:
                self.supabase_async_client = await create_async_client(
                    supabase_url=self.supabase_url, supabase_key=self.supabase_anon_key
                )
                logger.info("✅ Supabase async client initialized for realtime")
            except Exception as e:
                logger.error(f"❌ Failed to initialize async client: {e}")
                return

        if not self.supabase_async_client:
            logger.warning(
                "Cannot start subscriptions: Supabase async client not initialized"
            )
            return

        try:
            # Subscribe to accounts table
            await self._subscribe_to_table("accounts", self._handle_account_change)

            # Subscribe to transactions table
            await self._subscribe_to_table(
                "transactions", self._handle_transaction_change
            )

            # Subscribe to categories table
            await self._subscribe_to_table("categories", self._handle_category_change)

            logger.info("All real-time subscriptions started")
        except Exception as e:
            logger.error(f"Failed to start subscriptions: {e}")

    async def _subscribe_to_table(self, table_name: str, handler):
        """Subscribe to a specific table changes."""
        if not self.supabase_async_client:
            logger.warning(
                f"Cannot subscribe to {table_name}: Supabase async client not initialized"
            )
            return

        try:
            # Get the realtime channel from async client
            realtime = self.supabase_async_client.realtime

            # Create channel for the table
            channel = realtime.channel(f"public:{table_name}")

            # Subscribe to INSERT events
            channel.on_postgres_changes(
                event="INSERT",
                schema="public",
                table=table_name,
                callback=lambda payload: asyncio.create_task(
                    self._handle_realtime_event(handler, "INSERT", payload)
                ),
            )

            # Subscribe to UPDATE events
            channel.on_postgres_changes(
                event="UPDATE",
                schema="public",
                table=table_name,
                callback=lambda payload: asyncio.create_task(
                    self._handle_realtime_event(handler, "UPDATE", payload)
                ),
            )

            # Subscribe to DELETE events
            channel.on_postgres_changes(
                event="DELETE",
                schema="public",
                table=table_name,
                callback=lambda payload: asyncio.create_task(
                    self._handle_realtime_event(handler, "DELETE", payload)
                ),
            )

            # Subscribe to the channel
            await channel.subscribe()

            # Store the subscription for cleanup
            self.subscriptions[table_name] = channel

            logger.info(f"✅ Successfully subscribed to {table_name} table changes")

        except Exception as e:
            logger.error(f"❌ Failed to subscribe to {table_name}: {e}")
            # Create a fallback polling mechanism if realtime fails
            logger.info(f"🔄 Setting up polling fallback for {table_name}")
            self._setup_polling_fallback(table_name, handler)

    async def _handle_realtime_event(
        self, handler, event_type: str, payload: Dict[str, Any]
    ):
        """Handle real-time events from Supabase."""
        try:
            # Convert Supabase realtime payload to expected format
            formatted_payload = {
                "eventType": event_type,
                "record": payload.get("new", {})
                if event_type != "DELETE"
                else payload.get("old", {}),
                "old_record": payload.get("old", {}),
                "table": payload.get("table", ""),
                "schema": payload.get("schema", "public"),
            }

            logger.info(
                f"📡 Real-time event received: {event_type} on {formatted_payload['table']}"
            )

            # Call the appropriate handler
            if handler:
                await handler(formatted_payload)

        except Exception as e:
            logger.error(f"❌ Error handling real-time event: {e}")

    def _setup_polling_fallback(self, table_name: str, handler):
        """Set up a polling fallback if real-time subscription fails."""
        # For now, just store the handler - can be extended to implement polling
        logger.warning(f"⚠️  Polling fallback not implemented for {table_name}")

    async def _handle_account_change(self, payload: Dict[str, Any]):
        """Handle account table changes."""
        try:
            event_type = payload.get("eventType", "UNKNOWN")
            record = payload.get("record", {})

            logger.info(f"Account change detected: {event_type}")

            # Broadcast to all connected clients
            await self._broadcast_event(
                {
                    "type": "account_change",
                    "event_type": event_type,
                    "data": record,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Error handling account change: {e}")

    async def _handle_transaction_change(self, payload: Dict[str, Any]):
        """Handle transaction table changes."""
        try:
            event_type = payload.get("eventType", "UNKNOWN")
            record = payload.get("record", {})
            table_name = payload.get("table", "transactions")

            logger.info(
                f"💳 Transaction {event_type} detected: {record.get('description', 'N/A')}"
            )

            # Create comprehensive event for frontend
            event = {
                "type": "transaction_change",
                "event_type": event_type,
                "table": table_name,
                "data": record,
                "timestamp": datetime.utcnow().isoformat(),
                "requires_chart_update": True,  # Flag for frontend to update charts
                "requires_table_update": True,  # Flag for frontend to update data table
            }

            # Broadcast to all connected clients
            await self._broadcast_event(event)

            # Also trigger a general data refresh to ensure charts are updated
            await self.trigger_data_refresh("transactions")

        except Exception as e:
            logger.error(f"❌ Error handling transaction change: {e}")

    async def _handle_category_change(self, payload: Dict[str, Any]):
        """Handle category table changes."""
        try:
            event_type = payload.get("eventType", "UNKNOWN")
            record = payload.get("record", {})

            logger.info(f"Category change detected: {event_type}")

            # Broadcast to all connected clients
            await self._broadcast_event(
                {
                    "type": "category_change",
                    "event_type": event_type,
                    "data": record,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Error handling category change: {e}")

    async def _broadcast_event(self, event: Dict[str, Any]):
        """Broadcast event to all connected WebSocket clients."""
        if not self.websockets:
            return

        message = json.dumps(event)
        disconnected_sessions = []

        for session_id, websocket in self.websockets.items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send to session {session_id}: {e}")
                disconnected_sessions.append(session_id)

        # Clean up disconnected websockets
        for session_id in disconnected_sessions:
            await self.unregister_websocket(session_id)

    def register_websocket(self, session_id: str, websocket: Any):
        """Register a WebSocket connection."""
        self.websockets[session_id] = websocket
        self.active_sessions.add(session_id)
        logger.info(f"WebSocket registered for session {session_id}")

    async def unregister_websocket(self, session_id: str):
        """Unregister a WebSocket connection."""
        if session_id in self.websockets:
            del self.websockets[session_id]
        if session_id in self.active_sessions:
            self.active_sessions.remove(session_id)
        logger.info(f"WebSocket unregistered for session {session_id}")

    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status."""
        return {
            "supabase_connected": self.supabase_client is not None,
            "active_subscriptions": list(self.subscriptions.keys()),
            "connected_sessions": len(self.active_sessions),
            "active_websockets": len(self.websockets),
        }

    async def trigger_data_refresh(self, data_type: str = "all"):
        """Manually trigger a data refresh for all connected clients."""
        event = {
            "type": "data_refresh",
            "data_type": data_type,
            "timestamp": datetime.utcnow().isoformat(),
            "requires_chart_update": True,
            "requires_table_update": True,
            "auto_triggered": False,  # Indicate this was a manual refresh
        }

        logger.info(f"🔄 Triggering data refresh for: {data_type}")
        await self._broadcast_event(event)

    async def cleanup(self):
        """Cleanup resources."""
        # Close all WebSocket connections
        for session_id in list(self.websockets.keys()):
            await self.unregister_websocket(session_id)

        # Cancel subscriptions
        self.subscriptions.clear()

        logger.info("Realtime service cleaned up")


# Global instance
realtime_service = RealtimeService()
