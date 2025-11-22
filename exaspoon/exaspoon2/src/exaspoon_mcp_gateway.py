import asyncio
import os
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from fastmcp import FastMCP
from pydantic import BaseModel
from supabase import Client, create_client

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
# Add spoon-core to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "spoon-core"))

# Initialize FastMCP server
mcp = FastMCP("Exaspoon Database MCP")

import dotenv

dotenv.load_dotenv()


# Configuration
@dataclass
class AppConfig:
    supabase_url: str
    supabase_service_key: str
    openai_api_key: str
    openai_base_url: Optional[str] = None
    embedding_model: str = "text-embedding-3-large"
    log_level: str = "info"

    @classmethod
    def from_env(cls) -> "AppConfig":
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY", "")
        openai_api_key = os.getenv("OPENAI_API_KEY", "")

        # Validate required environment variables
        if not supabase_url:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not supabase_service_key:
            raise ValueError("SUPABASE_SERVICE_KEY environment variable is required")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        return cls(
            supabase_url=supabase_url,
            supabase_service_key=supabase_service_key,
            openai_api_key=openai_api_key,
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
            log_level=os.getenv("LOG_LEVEL", "info"),
        )


# Enums
class TransactionDirection(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class CategoryKind(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class AccountType(Enum):
    ONCHAIN = "onchain"
    OFFCHAIN = "offchain"


# Data Models
@dataclass
class CreateTransactionInput:
    account_id: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    direction: Optional[TransactionDirection] = None
    occurred_at: Optional[str] = None
    description: Optional[str] = None
    raw_source: Optional[str] = None


@dataclass
class SearchSimilarInput:
    query: str
    limit: Optional[int] = None


@dataclass
class UpsertCategoryInput:
    name: str
    kind: Optional[CategoryKind] = None
    description: Optional[str] = None


@dataclass
class ListAccountsInput:
    type: Optional[AccountType] = None
    search: Optional[str] = None


@dataclass
class UpsertAccountInput:
    name: str
    type: AccountType
    currency: str
    network: Optional[str] = None
    institution: Optional[str] = None


@dataclass
class UpsertPlanInput:
    period_start: str
    period_end: str
    category_id: Optional[str] = None
    account_id: Optional[str] = None
    amount: float = 0.0
    currency: str = "USD"


@dataclass
class ListPlansInput:
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    category_id: Optional[str] = None
    account_id: Optional[str] = None
    currency: Optional[str] = None


# Supabase Client
class SupabaseClient:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client: Client = create_client(
            config.supabase_url, config.supabase_service_key
        )

    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.table(table).insert(data).execute()
        return response.data[0] if response.data else {}

    async def update(self, table: str, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        response = self.client.table(table).update(data).eq("id", id).execute()
        return response.data[0] if response.data else {}

    async def select(
        self, table: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        query = self.client.table(table).select("*")

        if filters:
            # Separate special parameters from regular filters
            order_value = None
            limit_value = None
            regular_filters = {}

            for key, value in filters.items():
                if key == "order":
                    order_value = value
                elif key == "limit":
                    limit_value = value
                else:
                    regular_filters[key] = value

            # Apply order before filters (Supabase requires order before eq)
            if order_value:
                if "." in order_value:
                    column, direction = order_value.split(".", 1)
                    if direction.lower() == "desc":
                        query = query.order(column, desc=True)
                    else:
                        query = query.order(column)
                else:
                    # If no direction specified, default to asc
                    query = query.order(order_value)

            # Apply regular filters (eq, etc.)
            for key, value in regular_filters.items():
                query = query.eq(key, value)

            # Apply limit last
            if limit_value:
                query = query.limit(int(limit_value))

        response = query.execute()
        return response.data if response.data else []

    async def rpc(self, function: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        response = self.client.rpc(function, data).execute()
        return response.data if response.data else []


# Embedding Service
class EmbeddingService:
    def __init__(self, config: AppConfig):
        self.config = config
        self.base_url = config.openai_base_url or "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {config.openai_api_key}",
            "Content-Type": "application/json",
        }

    async def embed(self, text: str) -> List[float]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json={
                    "model": self.config.embedding_model,
                    "input": text,
                },
            )
            response.raise_for_status()
            result = response.json()

            # Handle different response formats
            if (
                "data" in result
                and isinstance(result["data"], list)
                and len(result["data"]) > 0
            ):
                embedding = result["data"][0]["embedding"]
                # Ensure it's a list of floats
                if isinstance(embedding, list):
                    return [
                        float(x) if isinstance(x, (int, float)) else 0.0
                        for x in embedding
                    ]
                else:
                    # If it's not a list, convert to a list of floats
                    return [float(embedding)] if embedding else []
            else:
                # Fallback: try to extract embedding directly
                if "embedding" in result:
                    embedding = result["embedding"]
                    if isinstance(embedding, list):
                        return [
                            float(x) if isinstance(x, (int, float)) else 0.0
                            for x in embedding
                        ]
                    else:
                        return [float(embedding)] if embedding else []
                else:
                    # Return empty embedding if format is unexpected
                    print(f"Warning: Unexpected embedding response format: {result}")
                    return []

    async def maybe_embed(self, text: Optional[str]) -> Optional[List[float]]:
        if text and text.strip():
            return await self.embed(text)
        return None


# Database Service
class DatabaseService:
    def __init__(self, config: AppConfig):
        self.supabase = SupabaseClient(config)
        self.embedding = EmbeddingService(config)

    async def insert_transaction(
        self, input: CreateTransactionInput, embedding: Optional[List[float]]
    ) -> Dict[str, Any]:
        payload = {
            "account_id": input.account_id,
            "amount": input.amount,
            "currency": input.currency,
            "direction": input.direction.value,
            "occurred_at": input.occurred_at,
            "description": input.description,
            "raw_source": input.raw_source,
            "embedding": embedding,
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        result = await self.supabase.insert("transactions", payload)
        return result

    async def upsert_category(
        self, input: UpsertCategoryInput, embedding: Optional[List[float]]
    ) -> Dict[str, Any]:
        description = input.description or input.name
        payload = {
            "name": input.name,
            "kind": input.kind.value if input.kind else CategoryKind.EXPENSE.value,
            "description": description,
            "embedding": embedding,
        }

        # Check if category exists
        existing = await self.supabase.select("categories", {"name": input.name})

        if existing:
            # Update existing category
            category_id = existing[0]["id"]
            await self.supabase.update("categories", category_id, payload)
            result = await self.supabase.select("categories", {"id": category_id})
            return result[0] if result else {}
        else:
            # Create new category
            return await self.supabase.insert("categories", payload)

    async def upsert_account(self, input: UpsertAccountInput) -> Dict[str, Any]:
        payload = {
            "name": input.name,
            "type": input.type.value,
            "currency": input.currency,
            "network": input.network,
            "institution": input.institution,
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        # Check if account exists
        existing = await self.supabase.select(
            "accounts", {"name": input.name, "type": input.type.value}
        )

        if existing:
            # Update existing account
            account_id = existing[0]["id"]
            await self.supabase.update("accounts", account_id, payload)
            result = await self.supabase.select("accounts", {"id": account_id})
            return result[0] if result else {}
        else:
            # Create new account
            return await self.supabase.insert("accounts", payload)

    async def list_accounts(self, params: ListAccountsInput) -> List[Dict[str, Any]]:
        filters = {"order": "name.asc"}

        if params.type:
            filters["type"] = params.type.value

        accounts = await self.supabase.select("accounts", filters)

        # Apply search filter if provided
        if params.search and params.search.strip():
            search_term = params.search.lower()
            accounts = [
                account
                for account in accounts
                if search_term in account.get("name", "").lower()
            ]

        return accounts

    async def search_similar_transactions(
        self, embedding: List[float], limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        limit = max(1, min(25, limit or 5))  # Clamp between 1 and 25

        result = await self.supabase.rpc(
            "search_similar_transactions",
            {
                "query_embedding": embedding,
                "match_count": limit,
            },
        )

        return result

    async def upsert_plan(self, input: UpsertPlanInput) -> Dict[str, Any]:
        payload = {
            "period_start": input.period_start,
            "period_end": input.period_end,
            "category_id": input.category_id,
            "account_id": input.account_id,
            "amount": input.amount,
            "currency": input.currency,
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        # Create new plan (plans table doesn't have unique constraints for upsert logic)
        return await self.supabase.insert("plans", payload)

    async def list_plans(self, params: ListPlansInput) -> List[Dict[str, Any]]:
        filters = {"order": "period_start.desc"}

        if params.period_start:
            filters["period_start"] = params.period_start

        if params.period_end:
            filters["period_end"] = params.period_end

        if params.category_id:
            filters["category_id"] = params.category_id

        if params.account_id:
            filters["account_id"] = params.account_id

        if params.currency:
            filters["currency"] = params.currency

        plans = await self.supabase.select("plans", filters)
        return plans

    async def search_similar_categories(
        self, embedding: List[float], limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        limit = max(1, min(25, limit or 5))  # Clamp between 1 and 25

        result = await self.supabase.rpc(
            "search_similar_categories",
            {
                "query_embedding": embedding,
                "match_count": limit,
            },
        )

        return result


# Output Models (Pydantic)
class CreateTransactionOutput(BaseModel):
    transaction: Dict[str, Any]


class SearchSimilarTransactionsOutput(BaseModel):
    matches: List[Dict[str, Any]]


class UpsertCategoryOutput(BaseModel):
    category: Dict[str, Any]


class SearchSimilarCategoriesOutput(BaseModel):
    matches: List[Dict[str, Any]]


class ListAccountsOutput(BaseModel):
    accounts: List[Dict[str, Any]]


class UpsertAccountOutput(BaseModel):
    account: Dict[str, Any]


# Initialize services
config = AppConfig.from_env()
db_service = DatabaseService(config)


# MCP Tools
@mcp.tool(
    name="create_transaction",
    description="Insert a transaction row, automatically embedding the description.",
)
async def create_transaction(
    account_id: str,
    amount: float,
    currency: str,
    direction: str,
    occurred_at: str,
    description: Optional[str] = None,
    raw_source: Optional[str] = None,
) -> Dict[str, Any]:
    """Insert a transaction row, automatically embedding the description."""
    try:
        # Parse direction
        try:
            direction_enum = TransactionDirection(direction.lower())
        except ValueError:
            raise ValueError(
                f"Invalid direction: {direction}. Must be one of: income, expense, transfer"
            )

        # Create input
        input_data = CreateTransactionInput(
            account_id=account_id,
            amount=amount,
            currency=currency,
            direction=direction_enum,
            occurred_at=occurred_at,
            description=description,
            raw_source=raw_source,
        )

        # Generate embedding for description if provided
        embedding = await db_service.embedding.maybe_embed(description)

        # Insert transaction
        result = await db_service.insert_transaction(input_data, embedding)

        return {"transaction": result}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(
    name="search_similar_transactions",
    description="Semantic nearest-neighbor search over historical transactions.",
)
async def search_similar_transactions(
    query: str, limit: Optional[int] = None
) -> Dict[str, Any]:
    """Semantic nearest-neighbor search over historical transactions."""
    try:
        if not query or not query.strip():
            return {"error": "Query must not be empty"}

        # Generate embedding for query
        embedding = await db_service.embedding.embed(query.strip())

        # Search for similar transactions
        matches = await db_service.search_similar_transactions(embedding, limit)

        return {"matches": matches}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(
    name="upsert_category",
    description="Create or update a category with embeddings for semantic search.",
)
async def upsert_category(
    name: str, kind: Optional[str] = None, description: Optional[str] = None
) -> Dict[str, Any]:
    """Create or update a category with embeddings for semantic search."""
    try:
        # Parse kind
        kind_enum = None
        if kind:
            try:
                kind_enum = CategoryKind(kind.lower())
            except ValueError:
                raise ValueError(
                    f"Invalid kind: {kind}. Must be one of: income, expense, transfer"
                )

        # Create input
        input_data = UpsertCategoryInput(
            name=name, kind=kind_enum, description=description
        )

        # Generate embedding for description
        description_source = description or name
        embedding = await db_service.embedding.embed(description_source)

        # Upsert category
        result = await db_service.upsert_category(input_data, embedding)

        return {"category": result}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(
    name="search_similar_categories",
    description="Semantic search across categories by embedding query.",
)
async def search_similar_categories(
    query: str, limit: Optional[int] = None
) -> Dict[str, Any]:
    """Semantic search across categories by embedding query."""
    try:
        if not query or not query.strip():
            return {"error": "Query must not be empty"}

        # Generate embedding for query
        embedding = await db_service.embedding.embed(query.strip())

        # Search for similar categories
        matches = await db_service.search_similar_categories(embedding, limit)

        return {"matches": matches}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(
    name="list_accounts",
    description="List accounts with optional filters by type or name substring.",
)
async def list_accounts(
    type: Optional[str] = None, search: Optional[str] = None
) -> Dict[str, Any]:
    """List accounts with optional filters by type or name substring."""
    try:
        # Parse type with mapping for common aliases
        type_enum = None
        if type:
            type_lower = type.lower()
            # Map common type aliases to valid enum values
            type_mapping = {
                "bank": "offchain",
                "crypto": "onchain",
                "blockchain": "onchain",
                "fiat": "offchain",
                "wallet": "onchain",  # wallet typically refers to crypto/onchain
            }
            # Apply mapping if needed
            if type_lower in type_mapping:
                type_lower = type_mapping[type_lower]

            try:
                type_enum = AccountType(type_lower)
            except ValueError:
                raise ValueError(
                    f"Invalid type: {type}. Must be one of: onchain, offchain (or aliases: bank/offchain, crypto/onchain, wallet/onchain)"
                )

        # Create input
        input_data = ListAccountsInput(type=type_enum, search=search)

        # List accounts
        accounts = await db_service.list_accounts(input_data)

        return {"accounts": accounts}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(
    name="upsert_account", description="Create or update an account keyed by name+type."
)
async def upsert_account(
    name: str,
    type: str,
    currency: str,
    network: Optional[str] = None,
    institution: Optional[str] = None,
) -> Dict[str, Any]:
    """Create or update an account keyed by name+type."""
    try:
        # Parse type with mapping for common aliases
        type_lower = type.lower()
        # Map common type aliases to valid enum values
        type_mapping = {
            "bank": "offchain",
            "crypto": "onchain",
            "blockchain": "onchain",
            "fiat": "offchain",
            "wallet": "onchain",  # wallet typically refers to crypto/onchain
        }
        # Apply mapping if needed
        if type_lower in type_mapping:
            type_lower = type_mapping[type_lower]

        try:
            type_enum = AccountType(type_lower)
        except ValueError:
            raise ValueError(
                f"Invalid type: {type}. Must be one of: onchain, offchain (or aliases: bank/offchain, crypto/onchain, wallet/onchain)"
            )

        # Create input
        input_data = UpsertAccountInput(
            name=name,
            type=type_enum,
            currency=currency,
            network=network,
            institution=institution,
        )

        # Generate embedding for name (not used in current implementation but kept for consistency)
        await db_service.embedding.embed(name)

        # Upsert account
        result = await db_service.upsert_account(input_data)

        return {"account": result}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(name="create_plan", description="Create a budget plan for a specific period.")
async def create_plan(
    period_start: str,
    period_end: str,
    amount: float,
    currency: str = "USD",
    account_id: Optional[str] = None,
    category_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a budget plan for a specific period."""
    try:
        # Create input
        input_data = UpsertPlanInput(
            period_start=period_start,
            period_end=period_end,
            amount=amount,
            currency=currency,
            account_id=account_id,
            category_id=category_id,
        )

        # Create plan
        result = await db_service.upsert_plan(input_data)

        return {"plan": result}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(name="list_plans", description="List budget plans with optional filters.")
async def list_plans(
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
    account_id: Optional[str] = None,
    category_id: Optional[str] = None,
    currency: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """List budget plans with optional filters."""
    try:
        # Create input
        input_data = ListPlansInput(
            period_start=period_start,
            period_end=period_end,
            account_id=account_id,
            category_id=category_id,
            currency=currency,
        )

        # List plans
        result = await db_service.list_plans(input_data)

        # Apply limit if provided
        if limit and limit > 0:
            result = result[:limit]

        return {"plans": result}
    except Exception as e:
        return {"error": str(e)}


# Main function to run the server
async def main():
    mcp_gateway_port = int(os.getenv("MCP_GATEWAY_PORT", "8766"))
    await mcp.run_async(transport="http", port=mcp_gateway_port)


if __name__ == "__main__":
    asyncio.run(main())
