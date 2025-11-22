"""
Script to seed test data for Exaspoon database tables.
Fills accounts, categories, and transactions with realistic test data.
"""

import asyncio
import os
from datetime import datetime, timedelta
from database import (
    AppConfig,
    DatabaseService,
    AccountType,
    CategoryKind,
    TransactionDirection,
    UpsertAccountInput,
    UpsertCategoryInput,
    CreateTransactionInput,
)

# Embedding configuration constants (from .env)
OPENAI_BASE_URL = "https://foundation-models.api.cloud.ru/v1"
EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-0.6B"


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
        UpsertCategoryInput(
            name="Crypto Mining",
            kind=CategoryKind.INCOME,
            description="Cryptocurrency mining rewards"
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


async def seed_transactions(
    db_service: DatabaseService,
    account_map: dict[str, str],
    category_map: dict[str, str]
) -> int:
    """Create test transactions and return count"""
    print("\nCreating test transactions...")

    base_date = datetime.now()

    transactions_data = [
        # Income transactions
        CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=5000.00,
            currency="USD",
            direction=TransactionDirection.INCOME,
            occurred_at=(base_date - timedelta(days=5)).isoformat(),
            description="Monthly salary payment from Tech Corp",
            raw_source="bank_statement_2024_01"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Ethereum Wallet"),
            amount=0.5,
            currency="ETH",
            direction=TransactionDirection.INCOME,
            occurred_at=(base_date - timedelta(days=10)).isoformat(),
            description="Ethereum mining reward",
            raw_source="blockchain_tx_0x123abc"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=1200.00,
            currency="USD",
            direction=TransactionDirection.INCOME,
            occurred_at=(base_date - timedelta(days=15)).isoformat(),
            description="Freelance project payment - Web Development",
            raw_source="invoice_2024_001"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Bitcoin Wallet"),
            amount=0.01,
            currency="BTC",
            direction=TransactionDirection.INCOME,
            occurred_at=(base_date - timedelta(days=20)).isoformat(),
            description="Bitcoin received from trading profits",
            raw_source="exchange_tx_btc_456"
        ),
        CreateTransactionInput(
            account_id=account_map.get("NEO Wallet"),
            amount=10.0,
            currency="NEO",
            direction=TransactionDirection.INCOME,
            occurred_at=(base_date - timedelta(days=22)).isoformat(),
            description="NEO blockchain staking reward - holding period completed",
            raw_source="neo_staking_reward_0xabc123"
        ),
        CreateTransactionInput(
            account_id=account_map.get("GAS Wallet"),
            amount=5.5,
            currency="GAS",
            direction=TransactionDirection.INCOME,
            occurred_at=(base_date - timedelta(days=21)).isoformat(),
            description="GAS tokens generated from NEO network participation",
            raw_source="neo_gas_generation_0xdef456"
        ),
        
        # Expense transactions
        CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=125.50,
            currency="USD",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=1)).isoformat(),
            description="Whole Foods Market - Grocery shopping",
            raw_source="card_payment_visa_789"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Credit Card"),
            amount=45.00,
            currency="USD",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=2)).isoformat(),
            description="Uber ride to airport",
            raw_source="uber_receipt_2024_01_15"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Credit Card"),
            amount=89.00,
            currency="USD",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=3)).isoformat(),
            description="Italian restaurant - dinner with friends",
            raw_source="restaurant_receipt_italian_123"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=15.99,
            currency="USD",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=4)).isoformat(),
            description="Netflix subscription monthly payment",
            raw_source="netflix_subscription_jan"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=250.00,
            currency="USD",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=6)).isoformat(),
            description="Doctor visit and prescription medication",
            raw_source="medical_bill_2024_01"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=299.00,
            currency="USD",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=7)).isoformat(),
            description="Online course - Advanced Python Programming",
            raw_source="udemy_course_purchase"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=120.00,
            currency="USD",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=8)).isoformat(),
            description="Electricity and internet bill",
            raw_source="utility_bill_january_2024"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Credit Card"),
            amount=199.99,
            currency="USD",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=9)).isoformat(),
            description="Amazon - New wireless headphones",
            raw_source="amazon_order_123456789"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=1800.00,
            currency="USD",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=12)).isoformat(),
            description="Monthly apartment rent payment",
            raw_source="rent_payment_january_2024"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Ethereum Wallet"),
            amount=0.1,
            currency="ETH",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=11)).isoformat(),
            description="Purchased USDT on Uniswap",
            raw_source="uniswap_swap_eth_usdt"
        ),
        CreateTransactionInput(
            account_id=account_map.get("EUR Bank Account"),
            amount=45.50,
            currency="EUR",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=13)).isoformat(),
            description="Coffee and pastries at local bakery",
            raw_source="bakery_payment_visa_eu"
        ),
        CreateTransactionInput(
            account_id=account_map.get("RUB Bank Account"),
            amount=3500.00,
            currency="RUB",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=14)).isoformat(),
            description="Grocery shopping at Perekrestok",
            raw_source="perekrestok_receipt_2024_01"
        ),
        CreateTransactionInput(
            account_id=account_map.get("NEO Wallet"),
            amount=2.0,
            currency="NEO",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=25)).isoformat(),
            description="NEO network transaction fee for smart contract deployment",
            raw_source="neo_contract_deployment_0x789xyz"
        ),
        CreateTransactionInput(
            account_id=account_map.get("GAS Wallet"),
            amount=1.5,
            currency="GAS",
            direction=TransactionDirection.EXPENSE,
            occurred_at=(base_date - timedelta(days=23)).isoformat(),
            description="GAS payment for NEO DApp interaction - DeFi protocol fee",
            raw_source="neo_defi_protocol_0xghi789"
        ),
        
        # Transfer transactions
        CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=500.00,
            currency="USD",
            direction=TransactionDirection.TRANSFER,
            occurred_at=(base_date - timedelta(days=16)).isoformat(),
            description="Transfer to Savings Account",
            raw_source="internal_transfer_checking_savings"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Ethereum Wallet"),
            amount=1000.00,
            currency="USDT",
            direction=TransactionDirection.TRANSFER,
            occurred_at=(base_date - timedelta(days=17)).isoformat(),
            description="Transferred USDT to Solana wallet",
            raw_source="cross_chain_transfer_eth_sol"
        ),
        CreateTransactionInput(
            account_id=account_map.get("Main Checking Account"),
            amount=200.00,
            currency="USD",
            direction=TransactionDirection.TRANSFER,
            occurred_at=(base_date - timedelta(days=18)).isoformat(),
            description="Payment to Credit Card account",
            raw_source="credit_card_payment_jan"
        ),
        CreateTransactionInput(
            account_id=account_map.get("NEO Wallet"),
            amount=3.0,
            currency="NEO",
            direction=TransactionDirection.TRANSFER,
            occurred_at=(base_date - timedelta(days=26)).isoformat(),
            description="Transfer NEO to external address for cross-chain swap",
            raw_source="neo_cross_chain_swap_0xjkl012"
        ),
        CreateTransactionInput(
            account_id=account_map.get("GAS Wallet"),
            amount=2.0,
            currency="GAS",
            direction=TransactionDirection.TRANSFER,
            occurred_at=(base_date - timedelta(days=27)).isoformat(),
            description="Bridge GAS tokens from NEO to BSC network",
            raw_source="neo_bsc_bridge_0xmno345"
        ),
    ]
    
    for i, transaction_input in enumerate(transactions_data, 1):
        embedding = await db_service.embedding.maybe_embed(transaction_input.description)
        result = await db_service.insert_transaction(transaction_input, embedding)
        transaction_id = result.get("id")
        print(f"  ✓ Created transaction {i}/{len(transactions_data)}: {transaction_input.description[:50]}... ({transaction_id})")

    return len(transactions_data)


async def main():
    """Main function to seed all test data"""
    print("=" * 60)
    print("Seeding Exaspoon Database with Test Data")
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
        
        # Seed transactions
        transaction_count = await seed_transactions(db_service, account_map, category_map)
        
        print("\n" + "=" * 60)
        print("✓ Successfully seeded all test data!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Accounts created: {len(account_map)}")
        print(f"  - Categories created: {len(category_map)}")
        print(f"  - Transactions created: {transaction_count}")
        
    except Exception as e:
        print(f"\n✗ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(main())

