"""
Script to seed only budget plans for existing accounts and categories.
Creates realistic budget plans for different periods without touching other tables.
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict
from database import (
    AppConfig,
    DatabaseService,
    UpsertPlanInput,
)

# Embedding configuration constants (from .env)
OPENAI_BASE_URL = "https://foundation-models.api.cloud.ru/v1"
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"


async def get_existing_data(db_service: DatabaseService) -> tuple[Dict[str, str], Dict[str, str]]:
    """Get existing accounts and categories from database"""
    print("Fetching existing accounts and categories...")

    # Get accounts
    accounts = await db_service.supabase.select("accounts", {"order": "name.asc"})
    account_map = {account["name"]: account["id"] for account in accounts}
    print(f"  Found {len(account_map)} accounts")

    # Get categories
    categories = await db_service.supabase.select("categories", {"order": "name.asc"})
    category_map = {category["name"]: category["id"] for category in categories}
    print(f"  Found {len(category_map)} categories")

    return account_map, category_map


async def seed_plans(db_service: DatabaseService, account_map: Dict[str, str], category_map: Dict[str, str]) -> Dict[str, str]:
    """Create realistic budget plans and return mapping of description -> id"""
    print("\nCreating budget plans...")

    current_date = datetime.now()
    plans_data = []

    # Monthly budget plans for different categories (next 6 months)
    monthly_budgets = [
        ("Groceries", 600.00, "USD", "Main Checking Account"),
        ("Transportation", 200.00, "USD", "Main Checking Account"),
        ("Restaurants", 300.00, "USD", "Credit Card"),
        ("Entertainment", 150.00, "USD", "Credit Card"),
        ("Utilities", 250.00, "USD", "Main Checking Account"),
        ("Healthcare", 100.00, "USD", "Main Checking Account"),
        ("Shopping", 250.00, "USD", "Credit Card"),
        ("Rent", 2000.00, "USD", "Main Checking Account"),
    ]

    # Create monthly budgets for each of the next 6 months
    for month_offset in range(6):
        month_start = (current_date.replace(day=1) + timedelta(days=month_offset * 31)).replace(day=1)

        # Get the last day of the month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

        for category_name, budget_amount, currency, account_name in monthly_budgets:
            if category_name in category_map and account_name in account_map:
                plans_data.append(UpsertPlanInput(
                    period_start=month_start.date().isoformat(),
                    period_end=month_end.date().isoformat(),
                    category_id=category_map[category_name],
                    account_id=account_map[account_name],
                    amount=budget_amount,
                    currency=currency
                ))

    # Quarterly savings and investment plans
    for quarter in range(1, 5):
        quarter_start = datetime(current_date.year, ((quarter - 1) * 3) + 1, 1).date()
        quarter_end = datetime(current_date.year, quarter * 3, 1).date() + timedelta(days=-1)

        if "Salary" in category_map and "Savings Account" in account_map:
            plans_data.append(UpsertPlanInput(
                period_start=quarter_start.isoformat(),
                period_end=quarter_end.isoformat(),
                category_id=category_map["Salary"],
                account_id=account_map["Savings Account"],
                amount=3000.00,  # Quarterly savings goal
                currency="USD"
            ))

        if "Investment Returns" in category_map and "Ethereum Wallet" in account_map:
            plans_data.append(UpsertPlanInput(
                period_start=quarter_start.isoformat(),
                period_end=quarter_end.isoformat(),
                category_id=category_map["Investment Returns"],
                account_id=account_map["Ethereum Wallet"],
                amount=1500.00,  # Quarterly crypto investment
                currency="USD"
            ))

    # Annual plans
    year_start = datetime(current_date.year, 1, 1).date()
    year_end = datetime(current_date.year, 12, 31).date()

    if "Rent" in category_map and "Main Checking Account" in account_map:
        plans_data.append(UpsertPlanInput(
            period_start=year_start.isoformat(),
            period_end=year_end.isoformat(),
            category_id=category_map["Rent"],
            account_id=account_map["Main Checking Account"],
            amount=24000.00,  # Annual rent budget ($2000/month)
            currency="USD"
        ))

    if "Freelance" in category_map and "Main Checking Account" in account_map:
        plans_data.append(UpsertPlanInput(
            period_start=year_start.isoformat(),
            period_end=year_end.isoformat(),
            category_id=category_map["Freelance"],
            account_id=account_map["Main Checking Account"],
            amount=12000.00,  # Annual freelance income goal
            currency="USD"
        ))

    # Crypto-specific plans (current month)
    crypto_month_start = current_date.replace(day=1)
    if crypto_month_start.month == 12:
        crypto_month_end = crypto_month_start.replace(year=crypto_month_start.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        crypto_month_end = crypto_month_start.replace(month=crypto_month_start.month + 1, day=1) - timedelta(days=1)

    if "Crypto Trading" in category_map and "Bitcoin Wallet" in account_map:
        plans_data.append(UpsertPlanInput(
            period_start=crypto_month_start.date().isoformat(),
            period_end=crypto_month_end.date().isoformat(),
            category_id=category_map["Crypto Trading"],
            account_id=account_map["Bitcoin Wallet"],
            amount=500.00,
            currency="USD"
        ))

    if "Crypto Mining" in category_map and "NEO Wallet" in account_map:
        plans_data.append(UpsertPlanInput(
            period_start=crypto_month_start.date().isoformat(),
            period_end=crypto_month_end.date().isoformat(),
            category_id=category_map["Crypto Mining"],
            account_id=account_map["NEO Wallet"],
            amount=100.00,
            currency="USD"
        ))

    # International accounts plans (current month)
    if "Groceries" in category_map:
        if "EUR Bank Account" in account_map:
            plans_data.append(UpsertPlanInput(
                period_start=crypto_month_start.date().isoformat(),
                period_end=crypto_month_end.date().isoformat(),
                category_id=category_map["Groceries"],
                account_id=account_map["EUR Bank Account"],
                amount=400.00,
                currency="EUR"
            ))

        if "RUB Bank Account" in account_map:
            plans_data.append(UpsertPlanInput(
                period_start=crypto_month_start.date().isoformat(),
                period_end=crypto_month_end.date().isoformat(),
                category_id=category_map["Groceries"],
                account_id=account_map["RUB Bank Account"],
                amount=15000.00,
                currency="RUB"
            ))

    # Insert all plans
    plan_map = {}
    for i, plan_input in enumerate(plans_data):
        try:
            result = await db_service.upsert_plan(plan_input)
            plan_id = result.get("id")
            if plan_id:
                # Create a descriptive key for the plan
                category_name = "Unknown"
                if plan_input.category_id:
                    for name, id in category_map.items():
                        if id == plan_input.category_id:
                            category_name = name
                            break

                account_name = "Unknown"
                if plan_input.account_id:
                    for name, id in account_map.items():
                        if id == plan_input.account_id:
                            account_name = name
                            break

                plan_key = f"{category_name} - {account_name} - {plan_input.period_start[:7]}"
                plan_map[plan_key] = plan_id

                # Show progress for first few and every 20th plan
                if i < 5 or (i + 1) % 20 == 0:
                    print(f"  ✓ Created plan #{i+1}: {plan_key} ({plan_id})")
        except Exception as e:
            print(f"  ✗ Error creating plan #{i+1}: {e}")

    print(f"  ✓ Total budget plans created: {len(plan_map)}")
    return plan_map


async def main():
    """Main function to seed only plans"""
    print("=" * 60)
    print("Seeding Budget Plans Only")
    print("=" * 60)

    try:
        # Override embedding configuration with constants
        os.environ["OPENAI_BASE_URL"] = OPENAI_BASE_URL
        os.environ["EMBEDDING_MODEL"] = EMBEDDING_MODEL

        # Initialize database service
        config = AppConfig.from_env()
        db_service = DatabaseService(config)

        print(f"\nEmbedding configuration:")
        print(f"  - Base URL: {config.openai_base_url}")
        print(f"  - Model: {config.embedding_model}")

        # Get existing data
        account_map, category_map = await get_existing_data(db_service)

        if not account_map:
            print("❌ No accounts found! Please run the full seeding script first.")
            return

        if not category_map:
            print("❌ No categories found! Please run the full seeding script first.")
            return

        # Seed plans
        plan_map = await seed_plans(db_service, account_map, category_map)

        print("\n" + "=" * 60)
        print("✓ Successfully seeded budget plans!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Existing accounts used: {len(account_map)}")
        print(f"  - Existing categories used: {len(category_map)}")
        print(f"  - Plans created: {len(plan_map)}")
        print(f"  - Plans cover: Next 6 months + quarterly + annual")

        # Show some example plans
        print(f"\nExample plans created:")
        for i, plan_key in enumerate(list(plan_map.keys())[:5]):
            print(f"  {i+1}. {plan_key}")

    except Exception as e:
        print(f"\n✗ Error seeding plans: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())