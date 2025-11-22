"""
Enhanced script to seed test data for Exaspoon database tables.
Fills accounts, categories, and transactions with realistic test data for one year.
Generates ~1000+ transactions based on real spending patterns.
"""

import asyncio
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from database import (
    AppConfig,
    DatabaseService,
    AccountType,
    CategoryKind,
    TransactionDirection,
    UpsertAccountInput,
    UpsertCategoryInput,
    UpsertPlanInput,
    CreateTransactionInput,
)

# Embedding configuration constants (from .env)
OPENAI_BASE_URL = "https://foundation-models.api.cloud.ru/v1"
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"

# Realistic transaction templates with min-max amounts
EXPENSE_TEMPLATES = {
    "Groceries": [
        ("Whole Foods Market", 80.50, 250.00),
        ("Trader Joe's", 45.30, 120.00),
        ("Safeway", 65.20, 180.00),
        ("Costco Wholesale", 150.00, 400.00),
        ("Local Farmers Market", 25.50, 85.00),
        ("Walmart Grocery", 55.00, 200.00),
        ("Target", 40.00, 150.00),
        ("CVS Pharmacy", 20.00, 80.00),
        ("Walgreens", 15.00, 60.00),
    ],
    "Transportation": [
        ("Uber ride", 12.50, 45.00),
        ("Lyft", 15.00, 35.00),
        ("Gas station", 40.00, 80.00),
        ("Public transport pass", 50.00, 120.00),
        ("Taxi to airport", 65.00, 120.00),
        ("Car wash", 15.00, 35.00),
        ("Parking meter", 5.00, 25.00),
        ("Uber Eats delivery", 8.00, 15.00),
        ("Gas for road trip", 60.00, 120.00),
    ],
    "Restaurants": [
        ("Italian restaurant dinner", 45.00, 120.00),
        ("Sushi bar", 60.00, 150.00),
        ("Coffee shop", 5.50, 25.00),
        ("Fast food", 12.00, 35.00),
        ("Bar with friends", 25.00, 80.00),
        ("Lunch at cafe", 18.00, 45.00),
        ("Food delivery", 22.00, 65.00),
        ("Pizza delivery", 25.00, 45.00),
        ("Brunch spot", 30.00, 75.00),
        ("Date night restaurant", 80.00, 200.00),
    ],
    "Entertainment": [
        ("Netflix subscription", 15.99, 19.99),
        ("Spotify Premium", 9.99, 14.99),
        ("Movie tickets", 25.00, 60.00),
        ("Concert tickets", 50.00, 200.00),
        ("Gaming subscription", 14.99, 59.99),
        ("Amazon Prime", 14.99, 14.99),
        ("Gym membership", 29.99, 80.00),
        ("Hulu subscription", 11.99, 14.99),
        ("Disney+ subscription", 12.99, 14.99),
        ("Apple TV+ subscription", 9.99, 9.99),
    ],
    "Utilities": [
        ("Electricity bill", 80.00, 200.00),
        ("Internet bill", 60.00, 120.00),
        ("Phone bill", 45.00, 100.00),
        ("Water bill", 30.00, 60.00),
        ("Gas bill", 50.00, 120.00),
        ("Streaming services bundle", 25.00, 50.00),
        ("Home security system", 30.00, 60.00),
        ("Garbage collection", 20.00, 40.00),
    ],
    "Healthcare": [
        ("Pharmacy prescription", 15.00, 150.00),
        ("Doctor visit copay", 25.00, 75.00),
        ("Dental cleaning", 100.00, 300.00),
        ("Eye exam", 50.00, 200.00),
        ("Health insurance premium", 200.00, 500.00),
        ("Physical therapy session", 40.00, 120.00),
        ("Specialist consultation", 75.00, 250.00),
        ("Medical lab tests", 50.00, 200.00),
    ],
    "Shopping": [
        ("Amazon order", 25.00, 300.00),
        ("Clothing store", 50.00, 250.00),
        ("Electronics purchase", 100.00, 800.00),
        ("Home goods", 35.00, 200.00),
        ("Books and media", 20.00, 100.00),
        ("Sporting goods", 40.00, 300.00),
        ("Hardware store", 15.00, 150.00),
        ("Department store", 60.00, 400.00),
        ("Online shopping", 30.00, 250.00),
    ],
    "Rent": [
        ("Monthly apartment rent", 1800.00, 3500.00),
        ("Home maintenance", 100.00, 500.00),
        ("Property tax", 200.00, 800.00),
        ("Home insurance", 50.00, 200.00),
    ],
}

INCOME_TEMPLATES = {
    "Salary": [
        ("Monthly salary payment", 4000.00, 8000.00),
        ("Bi-weekly paycheck", 1800.00, 4000.00),
        ("Performance bonus", 500.00, 3000.00),
        ("Year-end bonus", 2000.00, 10000.00),
        ("Quarterly bonus", 1000.00, 4000.00),
    ],
    "Freelance": [
        ("Web development project", 800.00, 5000.00),
        ("Design consultation", 300.00, 2000.00),
        ("Content writing gig", 150.00, 800.00),
        ("Marketing campaign", 500.00, 3000.00),
        ("Mobile app development", 1200.00, 8000.00),
        ("SEO optimization", 400.00, 2500.00),
    ],
    "Investment Returns": [
        ("Stock dividends", 50.00, 500.00),
        ("Crypto trading profit", 100.00, 2000.00),
        ("Bond interest", 25.00, 200.00),
        ("ETF distribution", 75.00, 400.00),
        ("Real estate rental income", 800.00, 2500.00),
    ],
    "Gifts": [
        ("Birthday gift from parents", 100.00, 500.00),
        ("Holiday gift", 50.00, 300.00),
        ("Wedding gift", 100.00, 1000.00),
        ("Cash gift", 25.00, 200.00),
    ],
}

CRYPTO_TEMPLATES = {
    "Crypto Trading": [
        ("ETH purchased on Uniswap", 0.1, 2.0, "ETH"),
        ("BTC trading profit", 0.001, 0.05, "BTC"),
        ("USDT swap", 100.00, 5000.00, "USDT"),
        ("SOL token purchase", 1.0, 50.0, "SOL"),
        ("DeFi yield farming", 50.00, 1000.00, "USDT"),
        ("Polygon network fees", 5.00, 50.00, "MATIC"),
    ],
    "Crypto Mining": [
        ("ETH mining reward", 0.001, 0.05, "ETH"),
        ("BTC mining reward", 0.0001, 0.005, "BTC"),
        ("NEO staking reward", 0.5, 5.0, "NEO"),
        ("GAS generation", 0.2, 3.0, "GAS"),
        ("Liquidity mining rewards", 10.00, 500.00, "USDT"),
        ("Smart contract deployment fee", 0.05, 0.5, "ETH"),
    ],
}

TRANSFER_TEMPLATES = [
    ("Transfer to Savings Account", 100.00, 1000.00, "USD"),
    ("Payment to Credit Card", 200.00, 2000.00, "USD"),
    ("Transfer between crypto exchanges", 50.00, 2000.00, "USDT"),
    ("Cross-chain bridge fee", 5.00, 50.00, "USDT"),
    ("Withdrawal to bank account", 500.00, 5000.00, "USD"),
]


class TransactionGenerator:
    """Generates realistic transactions over a one-year period"""

    def __init__(self, start_date: datetime):
        self.start_date = start_date
        self.current_date = start_date
        self.random = random.Random(42)  # For reproducible results

    def generate_amount(self, min_val: float, max_val: float) -> float:
        """Generate realistic amount using normal distribution"""
        mean = (min_val + max_val) / 2
        std_dev = (max_val - min_val) / 6  # ~99.7% within range
        amount = self.random.gauss(mean, std_dev)
        return round(max(min_val, min(max_val, amount)), 2)

    def should_transaction_happen(self, frequency: float) -> bool:
        """Determine if transaction should happen based on frequency (0-1)"""
        return self.random.random() < frequency

    def add_random_variation(self, base_date: datetime, max_days: int = 2) -> datetime:
        """Add small random variation to transaction date"""
        days_to_add = self.random.randint(-max_days, max_days)
        return base_date + timedelta(days=days_to_add)

    def generate_monthly_transactions(
        self,
        year: int,
        month: int,
        account_map: Dict[str, str]
    ) -> List[CreateTransactionInput]:
        """Generate transactions for a specific month"""
        transactions = []
        month_start = datetime(year, month, 1)

        # Income transactions (regular)
        if month in [1, 4, 7, 10]:  # Quarterly bonuses
            bonus_template = self.random.choice(INCOME_TEMPLATES["Salary"][2:])
            amount = self.generate_amount(*bonus_template[1:3])
            transactions.append(CreateTransactionInput(
                account_id=account_map.get("Main Checking Account"),
                amount=amount,
                currency="USD",
                direction=TransactionDirection.INCOME,
                occurred_at=month_start.replace(day=15).isoformat(),
                description=bonus_template[0],
                raw_source=f"bonus_payment_{year}_{month}"
            ))

        # Monthly salary
        salary_amount = self.generate_amount(*INCOME_TEMPLATES["Salary"][0][1:3])
        salary_day = self.random.choice([1, 15, 30])  # Random payday
        transactions.append(CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=salary_amount,
            currency="USD",
            direction=TransactionDirection.INCOME,
            occurred_at=month_start.replace(day=salary_day).isoformat(),
            description="Monthly salary payment",
            raw_source=f"salary_{year}_{month}"
        ))

        # Random freelance income (30% chance)
        if self.should_transaction_happen(0.3):
            freelance_template = self.random.choice(INCOME_TEMPLATES["Freelance"])
            amount = self.generate_amount(*freelance_template[1:3])
            transactions.append(CreateTransactionInput(
                account_id=account_map.get("Main Checking Account"),
                amount=amount,
                currency="USD",
                direction=TransactionDirection.INCOME,
                occurred_at=self.add_random_variation(month_start.replace(day=self.random.randint(5, 25))).isoformat(),
                description=freelance_template[0],
                raw_source=f"freelance_{year}_{month}"
            ))

        # Monthly rent
        rent_amount = self.generate_amount(*EXPENSE_TEMPLATES["Rent"][0][1:3])
        transactions.append(CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=rent_amount,
            currency="USD",
            direction=TransactionDirection.EXPENSE,
            occurred_at=month_start.replace(day=1).isoformat(),
            description="Monthly apartment rent",
            raw_source=f"rent_{year}_{month}"
        ))

        # Recurring monthly expenses
        recurring_expenses = [
            ("Netflix subscription", "Entertainment", 15.99),
            ("Spotify Premium", "Entertainment", 14.99),
            ("Amazon Prime", "Entertainment", 14.99),
            ("Gym membership", "Entertainment", 49.99),
            ("Internet bill", "Utilities", 79.99),
            ("Phone bill", "Utilities", 65.00),
        ]

        for expense_name, category, amount in recurring_expenses:
            transactions.append(CreateTransactionInput(
                account_id=account_map.get("Main Checking Account"),
                amount=amount,
                currency="USD",
                direction=TransactionDirection.EXPENSE,
                occurred_at=self.add_random_variation(month_start.replace(day=self.random.randint(1, 5))).isoformat(),
                description=expense_name,
                raw_source=f"{category.lower()}_{year}_{month}"
            ))

        # Variable expenses
        for week in range(1, 5):
            week_date = month_start + timedelta(weeks=week-1, days=self.random.randint(0, 6))

            # Groceries (1-2 times per week)
            if self.should_transaction_happen(0.8):
                grocery_template = self.random.choice(EXPENSE_TEMPLATES["Groceries"])
                amount = self.generate_amount(*grocery_template[1:3])
                transactions.append(CreateTransactionInput(
                    account_id=account_map.get("Main Checking Account"),
                    amount=amount,
                    currency="USD",
                    direction=TransactionDirection.EXPENSE,
                    occurred_at=week_date.isoformat(),
                    description=grocery_template[0],
                    raw_source=f"grocery_{year}_{month}_week{week}"
                ))

            # Restaurants (2-4 times per week)
            if self.should_transaction_happen(0.6):
                restaurant_template = self.random.choice(EXPENSE_TEMPLATES["Restaurants"])
                amount = self.generate_amount(*restaurant_template[1:3])
                transactions.append(CreateTransactionInput(
                    account_id=account_map.get("Credit Card"),
                    amount=amount,
                    currency="USD",
                    direction=TransactionDirection.EXPENSE,
                    occurred_at=week_date.isoformat(),
                    description=restaurant_template[0],
                    raw_source=f"restaurant_{year}_{month}_week{week}"
                ))

            # Transportation
            if self.should_transaction_happen(0.7):
                transport_template = self.random.choice(EXPENSE_TEMPLATES["Transportation"])
                amount = self.generate_amount(*transport_template[1:3])
                transactions.append(CreateTransactionInput(
                    account_id=account_map.get("Credit Card"),
                    amount=amount,
                    currency="USD",
                    direction=TransactionDirection.EXPENSE,
                    occurred_at=week_date.isoformat(),
                    description=transport_template[0],
                    raw_source=f"transport_{year}_{month}_week{week}"
                ))

        # Shopping (random 2-4 times per month)
        shopping_count = self.random.randint(2, 4)
        for _ in range(shopping_count):
            shopping_template = self.random.choice(EXPENSE_TEMPLATES["Shopping"])
            amount = self.generate_amount(*shopping_template[1:3])
            shopping_date = month_start + timedelta(days=self.random.randint(1, 28))
            transactions.append(CreateTransactionInput(
                account_id=account_map.get("Credit Card"),
                amount=amount,
                currency="USD",
                direction=TransactionDirection.EXPENSE,
                occurred_at=shopping_date.isoformat(),
                description=shopping_template[0],
                raw_source=f"shopping_{year}_{month}"
            ))

        # Crypto transactions (random 1-3 times per month)
        crypto_count = self.random.randint(1, 3)
        for _ in range(crypto_count):
            if self.random.random() < 0.6:  # 60% trading, 40% mining
                category = "Crypto Trading"
                template = self.random.choice(CRYPTO_TEMPLATES["Crypto Trading"])
            else:
                category = "Crypto Mining"
                template = self.random.choice(CRYPTO_TEMPLATES["Crypto Mining"])

            if len(template) == 4:  # Crypto transaction
                desc, min_amount, max_amount, currency = template
                account = self._get_crypto_account(currency, account_map)
                if account:
                    amount = self.generate_amount(min_amount, max_amount)
                    transactions.append(CreateTransactionInput(
                        account_id=account,
                        amount=amount,
                        currency=currency,
                        direction=TransactionDirection.INCOME if self.random.random() < 0.6 else TransactionDirection.EXPENSE,
                        occurred_at=(month_start + timedelta(days=self.random.randint(1, 28))).isoformat(),
                        description=desc,
                        raw_source=f"crypto_{year}_{month}"
                    ))

        # Transfers (1-2 times per month)
        transfer_count = self.random.randint(1, 2)
        for _ in range(transfer_count):
            transfer_template = self.random.choice(TRANSFER_TEMPLATES)
            desc, min_amount, max_amount, currency = transfer_template
            amount = self.generate_amount(min_amount, max_amount)

            if currency == "USD":
                account = account_map.get("Main Checking Account")
            else:
                account = self._get_crypto_account(currency, account_map)

            if account:
                transactions.append(CreateTransactionInput(
                    account_id=account,
                    amount=amount,
                    currency=currency,
                    direction=TransactionDirection.TRANSFER,
                    occurred_at=(month_start + timedelta(days=self.random.randint(5, 25))).isoformat(),
                    description=desc,
                    raw_source=f"transfer_{year}_{month}"
                ))

        return sorted(transactions, key=lambda x: x.occurred_at)

    def _get_crypto_account(self, currency: str, account_map: Dict[str, str]) -> str:
        """Get appropriate crypto account for currency"""
        crypto_mapping = {
            "ETH": "Ethereum Wallet",
            "BTC": "Bitcoin Wallet",
            "USDT": "USDT Wallet",
            "SOL": "Solana Wallet",
            "NEO": "NEO Wallet",
            "GAS": "GAS Wallet",
            "MATIC": "Ethereum Wallet",  # Use ETH wallet for MATRIC
        }
        account_name = crypto_mapping.get(currency)
        return account_map.get(account_name) if account_name else None


async def seed_accounts(db_service: DatabaseService) -> dict[str, str]:
    """Create test accounts and return mapping of name -> id"""
    print("Creating test accounts...")

    accounts_data = [
        # Offchain accounts
        UpsertAccountInput(
            name="Main Checking Account",
            type=AccountType.OFFCHAIN,
            currency="USD",
            institution="Chase Bank"
        ),
        UpsertAccountInput(
            name="Savings Account",
            type=AccountType.OFFCHAIN,
            currency="USD",
            institution="Chase Bank"
        ),
        UpsertAccountInput(
            name="Credit Card",
            type=AccountType.OFFCHAIN,
            currency="USD",
            institution="American Express"
        ),
        UpsertAccountInput(
            name="EUR Bank Account",
            type=AccountType.OFFCHAIN,
            currency="EUR",
            institution="Deutsche Bank"
        ),
        UpsertAccountInput(
            name="RUB Bank Account",
            type=AccountType.OFFCHAIN,
            currency="RUB",
            institution="Sberbank"
        ),
        # Onchain accounts
        UpsertAccountInput(
            name="Ethereum Wallet",
            type=AccountType.ONCHAIN,
            currency="ETH",
            network="ethereum"
        ),
        UpsertAccountInput(
            name="Bitcoin Wallet",
            type=AccountType.ONCHAIN,
            currency="BTC",
            network="bitcoin"
        ),
        UpsertAccountInput(
            name="USDT Wallet",
            type=AccountType.ONCHAIN,
            currency="USDT",
            network="ethereum"
        ),
        UpsertAccountInput(
            name="Solana Wallet",
            type=AccountType.ONCHAIN,
            currency="SOL",
            network="solana"
        ),
        UpsertAccountInput(
            name="NEO Wallet",
            type=AccountType.ONCHAIN,
            currency="NEO",
            network="neo"
        ),
        UpsertAccountInput(
            name="GAS Wallet",
            type=AccountType.ONCHAIN,
            currency="GAS",
            network="neo"
        ),
    ]

    account_map = {}
    for account_input in accounts_data:
        result = await db_service.upsert_account(account_input)
        account_id = result.get("id")
        account_name = account_input.name
        account_map[account_name] = account_id
        print(f"  ✓ Created account: {account_name} ({account_id})")

    return account_map


async def seed_plans(db_service: DatabaseService, account_map: dict[str, str], category_map: dict[str, str]) -> dict[str, str]:
    """Create realistic budget plans and return mapping of description -> id"""
    print("\nCreating budget plans...")

    current_date = datetime.now()

    # Budget plans for the next 12 months
    plans_data = []

    # Monthly budget plans for different categories
    monthly_budgets = [
        ("Groceries", 600.00, "USD"),
        ("Transportation", 200.00, "USD"),
        ("Restaurants", 300.00, "USD"),
        ("Entertainment", 150.00, "USD"),
        ("Utilities", 250.00, "USD"),
        ("Healthcare", 100.00, "USD"),
        ("Shopping", 250.00, "USD"),
    ]

    # Create monthly budgets for each of the next 6 months
    for month_offset in range(6):
        month_start = current_date.replace(day=1) + timedelta(days=month_offset * 30)
        # Get the last day of the month
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1) - timedelta(days=1)

        for category_name, budget_amount, currency in monthly_budgets:
            plans_data.append(UpsertPlanInput(
                period_start=month_start.date().isoformat(),
                period_end=month_end.date().isoformat(),
                category_id=category_map.get(category_name),
                account_id=account_map.get("Main Checking Account"),
                amount=budget_amount,
                currency=currency
            ))

    # Quarterly savings plans
    for quarter in range(1, 5):
        quarter_start = datetime(current_date.year, ((quarter - 1) * 3) + 1, 1).date()
        quarter_end = datetime(current_date.year, quarter * 3, 1).date() + timedelta(days=-1)

        plans_data.extend([
            UpsertPlanInput(
                period_start=quarter_start.isoformat(),
                period_end=quarter_end.isoformat(),
                category_id=category_map.get("Salary"),
                account_id=account_map.get("Savings Account"),
                amount=3000.00,  # Quarterly savings goal
                currency="USD"
            ),
            UpsertPlanInput(
                period_start=quarter_start.isoformat(),
                period_end=quarter_end.isoformat(),
                category_id=category_map.get("Investment Returns"),
                account_id=account_map.get("Ethereum Wallet"),
                amount=1500.00,  # Quarterly crypto investment
                currency="USD"
            ),
        ])

    # Annual plans
    year_start = datetime(current_date.year, 1, 1).date()
    year_end = datetime(current_date.year, 12, 31).date()

    plans_data.extend([
        UpsertPlanInput(
            period_start=year_start.isoformat(),
            period_end=year_end.isoformat(),
            category_id=category_map.get("Rent"),
            account_id=account_map.get("Main Checking Account"),
            amount=24000.00,  # Annual rent budget ($2000/month)
            currency="USD"
        ),
        UpsertPlanInput(
            period_start=year_start.isoformat(),
            period_end=year_end.isoformat(),
            category_id=category_map.get("Freelance"),
            account_id=account_map.get("Main Checking Account"),
            amount=12000.00,  # Annual freelance income goal
            currency="USD"
        ),
    ])

    # Crypto-specific plans
    crypto_month_start = current_date.replace(day=1)
    crypto_month_end = crypto_month_start.replace(day=28)

    plans_data.extend([
        UpsertPlanInput(
            period_start=crypto_month_start.date().isoformat(),
            period_end=crypto_month_end.date().isoformat(),
            category_id=category_map.get("Crypto Trading"),
            account_id=account_map.get("Bitcoin Wallet"),
            amount=500.00,
            currency="USD"
        ),
        UpsertPlanInput(
            period_start=crypto_month_start.date().isoformat(),
            period_end=crypto_month_end.date().isoformat(),
            category_id=category_map.get("Crypto Mining"),
            account_id=account_map.get("NEO Wallet"),
            amount=100.00,
            currency="USD"
        ),
    ])

    # International accounts plans
    eur_month_start = current_date.replace(day=1)
    eur_month_end = eur_month_start.replace(day=28)

    plans_data.append(UpsertPlanInput(
        period_start=eur_month_start.date().isoformat(),
        period_end=eur_month_end.date().isoformat(),
        category_id=category_map.get("Groceries"),
        account_id=account_map.get("EUR Bank Account"),
        amount=400.00,
        currency="EUR"
    ))

    rub_month_start = current_date.replace(day=1)
    rub_month_end = rub_month_start.replace(day=28)

    plans_data.append(UpsertPlanInput(
        period_start=rub_month_start.date().isoformat(),
        period_end=rub_month_end.date().isoformat(),
        category_id=category_map.get("Groceries"),
        account_id=account_map.get("RUB Bank Account"),
        amount=15000.00,
        currency="RUB"
    ))

    plan_map = {}
    for i, plan_input in enumerate(plans_data):
        try:
            result = await db_service.upsert_plan(plan_input)
            plan_id = result.get("id")
            if plan_id:
                # Create a descriptive key for the plan
                category_name = "Unknown"
                if plan_input.category_id:
                    # Find category name by ID (reverse lookup)
                    for name, id in category_map.items():
                        if id == plan_input.category_id:
                            category_name = name
                            break

                account_name = "Unknown"
                if plan_input.account_id:
                    # Find account name by ID (reverse lookup)
                    for name, id in account_map.items():
                        if id == plan_input.account_id:
                            account_name = name
                            break

                plan_key = f"{category_name} - {account_name} - {plan_input.period_start[:7]}"
                plan_map[plan_key] = plan_id

                # Show progress for first few and every 10th plan
                if i < 5 or (i + 1) % 10 == 0:
                    print(f"  ✓ Created plan #{i+1}: {plan_key} ({plan_id})")
        except Exception as e:
            print(f"  ✗ Error creating plan #{i+1}: {e}")

    print(f"  ✓ Total budget plans created: {len(plan_map)}")
    return plan_map


async def seed_categories(db_service: DatabaseService) -> dict[str, str]:
    """Create test categories and return mapping of name -> id"""
    print("\nCreating test categories...")

    categories_data = [
        # Expense categories
        UpsertCategoryInput(
            name="Groceries",
            kind=CategoryKind.EXPENSE,
            description="Food and grocery shopping"
        ),
        UpsertCategoryInput(
            name="Transportation",
            kind=CategoryKind.EXPENSE,
            description="Taxi, Uber, public transport, gas"
        ),
        UpsertCategoryInput(
            name="Restaurants",
            kind=CategoryKind.EXPENSE,
            description="Dining out, cafes, bars"
        ),
        UpsertCategoryInput(
            name="Entertainment",
            kind=CategoryKind.EXPENSE,
            description="Movies, concerts, games, subscriptions"
        ),
        UpsertCategoryInput(
            name="Healthcare",
            kind=CategoryKind.EXPENSE,
            description="Medical expenses, pharmacy, insurance"
        ),
        UpsertCategoryInput(
            name="Education",
            kind=CategoryKind.EXPENSE,
            description="Courses, books, online learning"
        ),
        UpsertCategoryInput(
            name="Utilities",
            kind=CategoryKind.EXPENSE,
            description="Electricity, water, internet, phone bills"
        ),
        UpsertCategoryInput(
            name="Shopping",
            kind=CategoryKind.EXPENSE,
            description="Clothing, electronics, general purchases"
        ),
        UpsertCategoryInput(
            name="Rent",
            kind=CategoryKind.EXPENSE,
            description="Housing rent or mortgage payments"
        ),
        UpsertCategoryInput(
            name="Crypto Trading",
            kind=CategoryKind.EXPENSE,
            description="Cryptocurrency purchases and trading fees"
        ),
        UpsertCategoryInput(
            name="Crypto Mining",
            kind=CategoryKind.INCOME,
            description="Cryptocurrency mining rewards"
        ),
        # Income categories
        UpsertCategoryInput(
            name="Salary",
            kind=CategoryKind.INCOME,
            description="Monthly salary from employer"
        ),
        UpsertCategoryInput(
            name="Freelance",
            kind=CategoryKind.INCOME,
            description="Freelance work and consulting income"
        ),
        UpsertCategoryInput(
            name="Investment Returns",
            kind=CategoryKind.INCOME,
            description="Dividends, interest, crypto gains"
        ),
        UpsertCategoryInput(
            name="Gifts",
            kind=CategoryKind.INCOME,
            description="Money received as gifts"
        ),
        # Transfer category
        UpsertCategoryInput(
            name="Account Transfer",
            kind=CategoryKind.TRANSFER,
            description="Transfers between accounts"
        ),
    ]

    category_map = {}
    for category_input in categories_data:
        result = await db_service.upsert_category(category_input, None)  # Embedding will be generated
        category_id = result.get("id")
        category_name = category_input.name
        category_map[category_name] = category_id
        print(f"  ✓ Created category: {category_name} ({category_id})")

    return category_map


async def seed_yearly_transactions(
    db_service: DatabaseService,
    account_map: dict[str, str],
    category_map: dict[str, str],
    months: int = 12
) -> int:
    """Create test transactions for specified number of months"""
    print(f"\nCreating test transactions for {months} months...")

    generator = TransactionGenerator(datetime.now() - timedelta(days=months*30))
    all_transactions = []

    for month_offset in range(months):
        target_date = datetime.now() - timedelta(days=(months-month_offset)*30)
        year = target_date.year
        month = target_date.month

        print(f"  Generating transactions for {year}-{month:02d}...")
        month_transactions = generator.generate_monthly_transactions(year, month, account_map)
        all_transactions.extend(month_transactions)

        print(f"    Generated {len(month_transactions)} transactions")

    print(f"\nInserting {len(all_transactions)} transactions into database...")

    # Process transactions in batches to avoid overwhelming the database
    batch_size = 50
    total_inserted = 0

    for i in range(0, len(all_transactions), batch_size):
        batch = all_transactions[i:i + batch_size]
        batch_embeddings = []

        # Insert transactions one by one with error handling
        for transaction in batch:
            try:
                # Generate embedding with timeout handling
                embedding = None
                try:
                    embedding = await asyncio.wait_for(
                        db_service.embedding.maybe_embed(transaction.description),
                        timeout=10.0  # 10 second timeout
                    )
                except asyncio.TimeoutError:
                    print(f"  ⚠ Embedding timeout, using None for: {transaction.description[:30]}...")
                except Exception as embed_error:
                    print(f"  ⚠ Embedding error: {embed_error}, using None")

                # Insert transaction
                result = await db_service.insert_transaction(transaction, embedding)
                transaction_id = result.get("id")
                if transaction_id:
                    total_inserted += 1

                # Show progress for first few and every 50th transaction
                if total_inserted <= 10 or total_inserted % 50 == 0:
                    status = "✓" if embedding else "⚠"
                    print(f"  {status} Created #{total_inserted}: {transaction.description[:35]}... ({transaction_id})")

            except Exception as e:
                print(f"  ✗ Error inserting transaction '{transaction.description[:30]}...': {e}")

        # Small delay between batches to avoid overwhelming the API
        await asyncio.sleep(0.5)

    return total_inserted


async def main():
    """Main function to seed all test data"""
    print("=" * 60)
    print("Seeding Exaspoon Database with Yearly Test Data")
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

        # Seed accounts
        account_map = await seed_accounts(db_service)

        # Seed categories
        category_map = await seed_categories(db_service)

        # Seed plans
        plan_map = await seed_plans(db_service, account_map, category_map)

        # Ask user how many months of data to generate
        months = 12  # Default to 12 months
        print(f"\nGenerating data for {months} months...")

        # Seed transactions
        transaction_count = await seed_yearly_transactions(db_service, account_map, category_map, months)

        print("\n" + "=" * 60)
        print("✓ Successfully seeded all test data!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Accounts created: {len(account_map)}")
        print(f"  - Categories created: {len(category_map)}")
        print(f"  - Plans created: {len(plan_map)}")
        print(f"  - Transactions created: {transaction_count}")
        print(f"  - Average transactions per month: {transaction_count // months if months > 0 else 0}")

    except Exception as e:
        print(f"\n✗ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())