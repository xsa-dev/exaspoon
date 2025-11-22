#!/usr/bin/env python3
"""
Test script to validate real-time subscriptions.
This script will test if the Supabase real-time connection is working properly.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from realtime_service import realtime_service

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_realtime_connection():
    """Test the real-time service connection and subscriptions."""
    logger.info("🧪 Testing Real-time Service...")

    try:
        # Test 1: Check initialization
        logger.info("1️⃣ Checking Supabase client initialization...")
        status = realtime_service.get_connection_status()
        logger.info(f"📊 Initial status: {status}")

        if not status["supabase_connected"]:
            logger.error(
                "❌ Supabase client not initialized - check environment variables"
            )
            return False

        # Test 2: Start subscriptions
        logger.info("2️⃣ Starting real-time subscriptions...")
        await realtime_service.start_subscriptions()

        # Wait a moment for subscriptions to initialize
        await asyncio.sleep(2)

        # Test 3: Check subscriptions status
        logger.info("3️⃣ Checking subscription status...")
        status = realtime_service.get_connection_status()
        logger.info(f"📊 After subscription status: {status}")

        if not status["active_subscriptions"]:
            logger.warning("⚠️ No active subscriptions - this might indicate an issue")
        else:
            logger.info(f"✅ Active subscriptions: {status['active_subscriptions']}")

        # Test 4: Test manual event broadcasting
        logger.info("4️⃣ Testing manual event broadcasting...")
        await realtime_service.trigger_data_refresh("test")

        logger.info("✅ Real-time service test completed successfully!")
        logger.info("📝 To test full functionality:")
        logger.info("   1. Ensure the database setup SQL has been run in Supabase")
        logger.info("   2. Start the web application")
        logger.info("   3. Create a new transaction in the database")
        logger.info("   4. Check if the chart updates automatically")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False


async def main():
    """Main test function."""
    logger.info("🚀 Starting Real-time Service Test")

    success = await test_realtime_connection()

    if success:
        logger.info("🎉 Test completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Test failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
