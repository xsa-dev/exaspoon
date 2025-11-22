//! Tests for data models and serialization.

use exaspoon_db_mcp::models::{
    AccountType, CategoryKind, CreateTransactionInput, ListAccountsInput, SearchSimilarInput,
    TransactionDirection, UpsertAccountInput, UpsertCategoryInput,
};
use serde_json;

mod common;

#[test]
fn test_transaction_direction_as_ref() {
    assert_eq!(TransactionDirection::Income.as_ref(), "income");
    assert_eq!(TransactionDirection::Expense.as_ref(), "expense");
    assert_eq!(TransactionDirection::Transfer.as_ref(), "transfer");
}

#[test]
fn test_category_kind_as_ref() {
    assert_eq!(CategoryKind::Income.as_ref(), "income");
    assert_eq!(CategoryKind::Expense.as_ref(), "expense");
    assert_eq!(CategoryKind::Transfer.as_ref(), "transfer");
}

#[test]
fn test_account_type_as_ref() {
    assert_eq!(AccountType::Onchain.as_ref(), "onchain");
    assert_eq!(AccountType::Offchain.as_ref(), "offchain");
}

#[test]
fn test_create_transaction_input_serialization() {
    let input = CreateTransactionInput {
        account_id: "acct-1".to_string(),
        amount: 42.0,
        currency: "USD".to_string(),
        direction: TransactionDirection::Expense,
        occurred_at: "2024-01-02T03:04:05Z".to_string(),
        description: Some("Coffee".to_string()),
        raw_source: Some("bank-api".to_string()),
    };

    let json = serde_json::to_value(&input).unwrap();
    assert_eq!(json["account_id"], "acct-1");
    assert_eq!(json["amount"], 42.0);
    assert_eq!(json["currency"], "USD");
    assert_eq!(json["direction"], "expense");
    assert_eq!(json["occurred_at"], "2024-01-02T03:04:05Z");
    assert_eq!(json["description"], "Coffee");
    assert_eq!(json["raw_source"], "bank-api");
}

#[test]
fn test_create_transaction_input_serialization_without_optional_fields() {
    let input = CreateTransactionInput {
        account_id: "acct-1".to_string(),
        amount: 42.0,
        currency: "USD".to_string(),
        direction: TransactionDirection::Expense,
        occurred_at: "2024-01-02T03:04:05Z".to_string(),
        description: None,
        raw_source: None,
    };

    let json = serde_json::to_value(&input).unwrap();
    assert_eq!(json["account_id"], "acct-1");
    assert_eq!(json["amount"], 42.0);
    assert_eq!(json["currency"], "USD");
    assert_eq!(json["direction"], "expense");
    assert_eq!(json["occurred_at"], "2024-01-02T03:04:05Z");
    assert!(json.get("description").is_none());
    assert!(json.get("raw_source").is_none());
}

#[test]
fn test_upsert_category_input_serialization() {
    let input = UpsertCategoryInput {
        name: "Food".to_string(),
        kind: Some(CategoryKind::Expense),
        description: Some("Food and dining expenses".to_string()),
    };

    let json = serde_json::to_value(&input).unwrap();
    assert_eq!(json["name"], "Food");
    assert_eq!(json["kind"], "expense");
    assert_eq!(json["description"], "Food and dining expenses");
}

#[test]
fn test_upsert_category_input_serialization_without_optional_fields() {
    let input = UpsertCategoryInput {
        name: "Food".to_string(),
        kind: None,
        description: None,
    };

    let json = serde_json::to_value(&input).unwrap();
    assert_eq!(json["name"], "Food");
    assert!(json.get("kind").is_none());
    assert!(json.get("description").is_none());
}

#[test]
fn test_upsert_account_input_serialization() {
    let input = UpsertAccountInput {
        name: "Checking".to_string(),
        r#type: AccountType::Offchain,
        currency: "USD".to_string(),
        network: Some("ethereum".to_string()),
        institution: Some("Test Bank".to_string()),
    };

    let json = serde_json::to_value(&input).unwrap();
    assert_eq!(json["name"], "Checking");
    assert_eq!(json["type"], "offchain");
    assert_eq!(json["currency"], "USD");
    assert_eq!(json["network"], "ethereum");
    assert_eq!(json["institution"], "Test Bank");
}

#[test]
fn test_upsert_account_input_serialization_without_optional_fields() {
    let input = UpsertAccountInput {
        name: "Checking".to_string(),
        r#type: AccountType::Offchain,
        currency: "USD".to_string(),
        network: None,
        institution: None,
    };

    let json = serde_json::to_value(&input).unwrap();
    assert_eq!(json["name"], "Checking");
    assert_eq!(json["type"], "offchain");
    assert_eq!(json["currency"], "USD");
    assert!(json.get("network").is_none());
    assert!(json.get("institution").is_none());
}

#[test]
fn test_list_accounts_input_serialization() {
    let input = ListAccountsInput {
        r#type: Some(AccountType::Onchain),
        search: Some("test".to_string()),
    };

    let json = serde_json::to_value(&input).unwrap();
    assert_eq!(json["type"], "onchain");
    assert_eq!(json["search"], "test");
}

#[test]
fn test_list_accounts_input_serialization_without_optional_fields() {
    let input = ListAccountsInput {
        r#type: None,
        search: None,
    };

    let json = serde_json::to_value(&input).unwrap();
    assert!(json.get("type").is_none());
    assert!(json.get("search").is_none());
}

#[test]
fn test_search_similar_input_serialization() {
    let input = SearchSimilarInput {
        query: "Coffee shop".to_string(),
        limit: Some(5),
    };

    let json = serde_json::to_value(&input).unwrap();
    assert_eq!(json["query"], "Coffee shop");
    assert_eq!(json["limit"], 5);
}

#[test]
fn test_search_similar_input_serialization_without_optional_fields() {
    let input = SearchSimilarInput {
        query: "Coffee shop".to_string(),
        limit: None,
    };

    let json = serde_json::to_value(&input).unwrap();
    assert_eq!(json["query"], "Coffee shop");
    assert!(json.get("limit").is_none());
}

#[test]
fn test_create_transaction_input_deserialization() {
    let json_str = r#"
    {
        "account_id": "acct-1",
        "amount": 42.0,
        "currency": "USD",
        "direction": "expense",
        "occurred_at": "2024-01-02T03:04:05Z",
        "description": "Coffee",
        "raw_source": "bank-api"
    }
    "#;

    let input: CreateTransactionInput = serde_json::from_str(json_str).unwrap();
    assert_eq!(input.account_id, "acct-1");
    assert_eq!(input.amount, 42.0);
    assert_eq!(input.currency, "USD");
    assert_eq!(input.direction, TransactionDirection::Expense);
    assert_eq!(input.occurred_at, "2024-01-02T03:04:05Z");
    assert_eq!(input.description, Some("Coffee".to_string()));
    assert_eq!(input.raw_source, Some("bank-api".to_string()));
}

#[test]
fn test_upsert_category_input_deserialization() {
    let json_str = r#"
    {
        "name": "Food",
        "kind": "expense",
        "description": "Food and dining expenses"
    }
    "#;

    let input: UpsertCategoryInput = serde_json::from_str(json_str).unwrap();
    assert_eq!(input.name, "Food");
    assert_eq!(input.kind, Some(CategoryKind::Expense));
    assert_eq!(input.description, Some("Food and dining expenses".to_string()));
}

#[test]
fn test_upsert_account_input_deserialization() {
    let json_str = r#"
    {
        "name": "Checking",
        "type": "offchain",
        "currency": "USD",
        "network": "ethereum",
        "institution": "Test Bank"
    }
    "#;

    let input: UpsertAccountInput = serde_json::from_str(json_str).unwrap();
    assert_eq!(input.name, "Checking");
    assert_eq!(input.r#type, AccountType::Offchain);
    assert_eq!(input.currency, "USD");
    assert_eq!(input.network, Some("ethereum".to_string()));
    assert_eq!(input.institution, Some("Test Bank".to_string()));
}
