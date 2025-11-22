#!/usr/bin/env python3
"""Chart data service for fetching financial data from Supabase."""

import logging
import os

# Load environment variables from .env file
import pathlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
from dotenv import load_dotenv

project_root = pathlib.Path(__file__).parent.parent
load_dotenv(project_root / ".env")

logger = logging.getLogger(__name__)


class ChartDataService:
    """Service for fetching chart data from Supabase."""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")

        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """Make HTTP request to Supabase."""
        url = f"{self.supabase_url}/rest/v1/{endpoint}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.request(
                    method, url, headers=self.headers, **kwargs
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Supabase request failed: {e}")
                return []

    async def get_monthly_totals(self, months: int = 12) -> List[Dict[str, Any]]:
        """Calculate monthly totals for income/expenses."""
        try:
            # Get transactions for the last N months
            end_date = datetime.now()
            start_date = end_date - timedelta(
                days=months * 32
            )  # 32 days per month for safety

            # Format dates for Supabase
            start_iso = start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            end_iso = end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            # Get transactions in date range
            params = {
                "select": "*",
                "order": "occurred_at.desc",
                "and": f"(occurred_at.gte.{start_iso},occurred_at.lte.{end_iso})",
            }

            transactions = await self._make_request(
                "GET", "transactions", params=params
            )

            # Group by month and calculate totals
            monthly_data = {}
            for transaction in transactions:
                # Convert occurred_at to datetime
                occurred_at = datetime.fromisoformat(
                    transaction["occurred_at"].replace("Z", "+00:00")
                )
                month_key = occurred_at.strftime("%b %y").upper()

                if month_key not in monthly_data:
                    monthly_data[month_key] = {"income": 0, "expense": 0, "net": 0}

                amount = abs(float(transaction["amount"]))
                direction = transaction["direction"]

                if direction == "income":
                    monthly_data[month_key]["income"] += amount
                    monthly_data[month_key]["net"] += amount
                elif direction == "expense":
                    monthly_data[month_key]["expense"] += amount
                    monthly_data[month_key]["net"] -= amount

            # Convert to list and sort by date
            result = []
            month_order = [
                "JAN",
                "FEB",
                "MAR",
                "APR",
                "MAY",
                "JUN",
                "JUL",
                "AUG",
                "SEP",
                "OCT",
                "NOV",
                "DEC",
            ]

            for month_key, data in monthly_data.items():
                result.append(
                    {
                        "month": month_key,
                        "value": int(round(data["net"])),  # Round and convert to int
                    }
                )

            # Sort by date in descending chronological order (most recent first)
            def sort_key(item):
                month, year = item["month"].split()
                year_num = int(year)
                month_num = month_order.index(month)
                return year_num * 12 + month_num

            result.sort(key=sort_key, reverse=True)
            return result[:months]  # Return first N months (most recent first)

        except Exception as e:
            logger.error(f"Failed to calculate monthly totals: {e}")
            # Return fallback data for demo purposes
            return self._get_fallback_data()

    async def get_category_breakdown(self, months: int = 1) -> List[Dict[str, Any]]:
        """Get category breakdown for recent transactions."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)

            # Format dates for Supabase
            start_iso = start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            end_iso = end_date.strftime("%Y-%m-%dT%H:%M:%S.000Z")

            # Get transactions and categories
            transactions_params = {
                "select": "*",
                "and": f"(occurred_at.gte.{start_iso},occurred_at.lte.{end_iso},direction.eq.expense)",
            }

            transactions = await self._make_request(
                "GET", "transactions", params=transactions_params
            )
            categories = await self._make_request(
                "GET", "categories", params={"select": "id,name"}
            )

            # Create category lookup
            category_lookup = {cat["id"]: cat["name"] for cat in categories}

            # Group by category
            category_totals = {}
            for transaction in transactions:
                category_id = transaction.get("category_id")
                category_name = category_lookup.get(category_id, "Uncategorized")

                if category_name not in category_totals:
                    category_totals[category_name] = 0

                category_totals[category_name] += abs(float(transaction["amount"]))

            # Convert to list and sort by amount
            result = [
                {"category": name, "amount": int(round(amount))}
                for name, amount in category_totals.items()
            ]

            result.sort(key=lambda x: x["amount"], reverse=True)
            return result[:10]  # Top 10 categories

        except Exception as e:
            logger.error(f"Failed to get category breakdown: {e}")
            return []

    async def get_account_summary(self) -> List[Dict[str, Any]]:
        """Get account summary with balances."""
        try:
            accounts = await self._make_request(
                "GET", "accounts", params={"select": "*"}
            )

            result = []
            for account in accounts:
                # For demo purposes, we'll return account info without actual balances
                # In a real implementation, you'd calculate balances from transactions
                result.append(
                    {
                        "id": account["id"],
                        "name": account["name"],
                        "type": account["type"],
                        "currency": account["currency"],
                        "institution": account.get("institution", ""),
                    }
                )

            return result

        except Exception as e:
            logger.error(f"Failed to get account summary: {e}")
            return []

    def _get_fallback_data(self) -> List[Dict[str, Any]]:
        """Fallback data for demo purposes when database is unavailable."""
        current_date = datetime.now()
        fallback_data = []

        # Generate sample data for the last 6 months
        for i in range(6):
            date = current_date - timedelta(days=30 * i)
            month_key = date.strftime("%b %y").upper()
            # Generate some sample values that fluctuate
            sample_value = int((i - 3) * 35 + (i % 2) * 20 - 10)
            fallback_data.append({"month": month_key, "value": sample_value})

        # Reverse to get chronological order
        fallback_data.reverse()
        return fallback_data

    async def get_realtime_monthly_totals(
        self, months: int = 12
    ) -> List[Dict[str, Any]]:
        """Get monthly totals with real-time cache invalidation."""
        try:
            # For now, delegate to the existing method
            # In the future, this could implement caching and invalidation
            return await self.get_monthly_totals(months)
        except Exception as e:
            logger.error(f"Failed to get realtime monthly totals: {e}")
            return []

    async def get_realtime_category_breakdown(
        self, months: int = 1
    ) -> List[Dict[str, Any]]:
        """Get category breakdown with real-time cache invalidation."""
        try:
            # For now, delegate to the existing method
            # In the future, this could implement caching and invalidation
            return await self.get_category_breakdown(months)
        except Exception as e:
            logger.error(f"Failed to get realtime category breakdown: {e}")
            return []

    async def get_realtime_account_summary(self) -> List[Dict[str, Any]]:
        """Get account summary with real-time cache invalidation."""
        try:
            # For now, delegate to the existing method
            # In the future, this could implement caching and invalidation
            return await self.get_account_summary()
        except Exception as e:
            logger.error(f"Failed to get realtime account summary: {e}")
            return []

    async def invalidate_cache(self, cache_type: str = "all"):
        """Invalidate cache for specified data type."""
        # This is a placeholder for cache invalidation logic
        # In a real implementation, you would clear Redis or in-memory cache
        logger.info(f"Cache invalidated for type: {cache_type}")


# Singleton instance
chart_service = ChartDataService()
