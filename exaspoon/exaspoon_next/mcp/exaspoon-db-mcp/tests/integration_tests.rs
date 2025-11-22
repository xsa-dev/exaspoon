//! Integration tests for complete MCP server functionality.

use exaspoon_db_mcp::{
    models::{
        AccountType, CategoryKind, CreateTransactionInput, ListAccountsInput, SearchSimilarInput,
        TransactionDirection, UpsertAccountInput, UpsertCategoryInput,
    },
    server::ExaspoonDbServer,
};
use rmcp::{
    handler::server::wrapper::Parameters,
    model::ErrorCode,
};
use serde_json::json;
use std::sync::Arc;

mod common;

#[tokio::test]
async fn test_server_create_transaction_with_description() {
    let db = Arc::new(common::MockDatabase::new());
    let embedder = Arc::new(common::MockEmbedder::new(vec![0.1, 0.2, 0.3]));
    let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

    let input = CreateTransactionInput {
        account_id: "acct-1".to_string(),
        amount: 42.0,
        currency: "USD".to_string(),
        direction: TransactionDirection::Expense,
        occurred_at: "2024-01-02T03:04:05Z".to_string(),
        description: Some("Coffee".to_string()),
        raw_source: Some("bank-api".to_string()),
    };

    let result = server
        .create_transaction(Parameters(input.clone()))
        .await
        .expect("tool call should succeed");

    let payload = result.structured_content.expect("structured payload");
    assert_eq!(payload["transaction"]["id"], "txn-default");

    let inserted = db.inserted_transactions();
    assert_eq!(inserted.len(), 1);
    assert_eq!(inserted[0].0.account_id, input.account_id);
    assert_eq!(inserted[0].0.amount, input.amount);
    assert_eq!(inserted[0].0.currency, input.currency);
    assert_eq!(inserted[0].0.direction, input.direction);
    assert_eq!(inserted[0].0.occurred_at, input.occurred_at);
    assert_eq!(inserted[0].0.description, input.description);
    assert_eq!(inserted[0].0.raw_source, input.raw_source);
    assert_eq!(inserted[0].1, Some(vec![0.1, 0.2, 0.3]));

    let calls = embedder.calls();
    assert_eq!(calls.len(), 1);
    assert_eq!(calls[0], "Coffee");
}

#[tokio::test]
async fn test_server_create_transaction_without_description() {
    let db = Arc::new(common::MockDatabase::new());
    let embedder = Arc::new(common::MockEmbedder::new(vec![0.4, 0.5, 0.6]));
    let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

    let input = CreateTransactionInput {
        account_id: "acct-2".to_string(),
        amount: 10.0,
        currency: "USD".to_string(),
        direction: TransactionDirection::Income,
        occurred_at: "2024-01-02T03:04:05Z".to_string(),
        description: None,
        raw_source: None,
    };

    let result = server
        .create_transaction(Parameters(input.clone()))
        .await
        .expect("tool call should succeed");

    let payload = result.structured_content.expect("structured payload");
    assert_eq!(payload["transaction"]["id"], "txn-default");

    let inserted = db.inserted_transactions();
    assert_eq!(inserted.len(), 1);
    assert_eq!(inserted[0].0.account_id, input.account_id);
    assert_eq!(inserted[0].0.amount, input.amount);
    assert_eq!(inserted[0].0.currency, input.currency);
    assert_eq!(inserted[0].0.direction, input.direction);
    assert_eq!(inserted[0].0.occurred_at, input.occurred_at);
    assert_eq!(inserted[0].0.description, input.description);
    assert_eq!(inserted[0].0.raw_source, input.raw_source);
    assert_eq!(inserted[0].1, None); // No embedding for empty description

    let calls = embedder.calls();
    assert_eq!(calls.len(), 0); // No embedder call for empty description
}

#[tokio::test]
async fn test_server_search_similar_transactions_with_query() {
    let db = Arc::new(common::MockDatabase::new());
    let embedder = Arc::new(common::MockEmbedder::new(vec![0.2, 0.4, 0.6]));
    let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

    // Configure mock database to return specific matches
    db.configure(|state| {
        state.transaction_matches = vec![
            json!({ "id": "txn-1", "description": "Coffee shop" }),
            json!({ "id": "txn-2", "description": "Cafe" }),
        ];
    });

    let input = SearchSimilarInput {
        query: "Coffee".to_string(),
        limit: Some(5),
    };

    let result = server
        .search_similar_transactions(Parameters(input.clone()))
        .await
        .expect("tool call should succeed");

    let payload = result.structured_content.expect("structured payload");
    assert_eq!(payload["matches"].as_array().unwrap().len(), 2);
    assert_eq!(payload["matches"][0]["id"], "txn-1");
    assert_eq!(payload["matches"][0]["description"], "Coffee shop");
    assert_eq!(payload["matches"][1]["id"], "txn-2");
    assert_eq!(payload["matches"][1]["description"], "Cafe");

    let calls = embedder.calls();
    assert_eq!(calls.len(), 1);
    assert_eq!(calls[0], "Coffee");

    let search_limits = db.transaction_search_limits();
    assert_eq!(search_limits.len(), 1);
    assert_eq!(search_limits[0], Some(5));
}

#[tokio::test]
async fn test_server_search_similar_transactions_with_empty_query() {
    let db = Arc::new(common::MockDatabase::new());
    let embedder = Arc::new(common::MockEmbedder::new(vec![0.1, 0.2, 0.3]));
    let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

    let input = SearchSimilarInput {
        query: "   ".to_string(), // Whitespace only
        limit: Some(5),
    };

    let result = server
        .search_similar_transactions(Parameters(input))
        .await;

    assert!(result.is_err());
    let err = result.unwrap_err();
    assert_eq!(err.code, ErrorCode::INVALID_PARAMS);
    assert!(err.message.contains("query must not be empty"));
}

#[tokio::test]
async fn test_server_upsert_category() {
    let db = Arc::new(common::MockDatabase::new());
    let embedder = Arc::new(common::MockEmbedder::new(vec![0.3, 0.6, 0.9]));
    let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

    let input = UpsertCategoryInput {
        name: "Food".to_string(),
        kind: Some(CategoryKind::Expense),
        description: Some("Food and dining expenses".to_string()),
    };

    let result = server
        .upsert_category(Parameters(input.clone()))
        .await
        .expect("tool call should succeed");

    let payload = result.structured_content.expect("structured payload");
    assert_eq!(payload["category"]["id"], "cat-default");

    let upserted = db.upserted_categories();
    assert_eq!(upserted.len(), 1);
    assert_eq!(upserted[0].0.name, input.name);
    assert_eq!(upserted[0].0.kind, input.kind);
    assert_eq!(upserted[0].0.description, input.description);
    assert_eq!(upserted[0].1, Some(vec![0.3, 0.6, 0.9]));

    let calls = embedder.calls();
    assert_eq!(calls.len(), 1);
    assert_eq!(calls[0], "Food and dining expenses"); // Description is used for embedding
}

#[tokio::test]
async fn test_server_upsert_category_without_description() {
    let db = Arc::new(common::MockDatabase::new());
    let embedder = Arc::new(common::MockEmbedder::new(vec![0.1, 0.2, 0.3]));
    let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

    let input = UpsertCategoryInput {
        name: "Food".to_string(),
        kind: Some(CategoryKind::Expense),
        description: None,
    };

    let result = server
        .upsert_category(Parameters(input.clone()))
        .await
        .expect("tool call should succeed");

    let payload = result.structured_content.expect("structured payload");
    assert_eq!(payload["category"]["id"], "cat-default");

    let upserted = db.upserted_categories();
    assert_eq!(upserted.len(), 1);
    assert_eq!(upserted[0].0.name, input.name);
    assert_eq!(upserted[0].0.kind, input.kind);
    assert_eq!(upserted[0].0.description, input.description);
    assert_eq!(upserted[0].1, Some(vec![0.1, 0.2, 0.3]));

    let calls = embedder.calls();
    assert_eq!(calls.len(), 1);
    assert_eq!(calls[0], "Food"); // Name is used for embedding when description is missing
}

#[tokio::test]
async fn test_server_search_similar_categories() {
    let db = Arc::new(common::MockDatabase::new());
    let embedder = Arc::new(common::MockEmbedder::new(vec![0.4, 0.8, 0.12]));
    let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

    // Configure mock database to return specific matches
    db.configure(|state| {
        state.category_matches = vec![
            json!({ "id": "cat-1", "name": "Food" }),
            json!({ "id": "cat-2", "name": "Dining" }),
        ];
    });

    let input = SearchSimilarInput {
        query: "Restaurant".to_string(),
        limit: Some(3),
    };

    let result = server
        .search_similar_categories(Parameters(input.clone()))
        .await
        .expect("tool call should succeed");

    let payload = result.structured_content.expect("structured payload");
    assert_eq!(payload["matches"].as_array().unwrap().len(), 2);
    assert_eq!(payload["matches"][0]["id"], "cat-1");
    assert_eq!(payload["matches"][0]["name"], "Food");
    assert_eq!(payload["matches"][1]["id"], "cat-2");
    assert_eq!(payload["matches"][1]["name"], "Dining");

    let calls = embedder.calls();
    assert_eq!(calls.len(), 1);
    assert_eq!(calls[0], "Restaurant");
}

#[tokio::test]
async fn test_server_search_similar_categories_with_empty_query() {
    let db = Arc::new(common::MockDatabase::new());
    let embedder = Arc::new(common::MockEmbedder::new(vec![0.1, 0.2, 0.3]));
    let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

    let input = SearchSimilarInput {
        query: "".to_string(), // Empty string
        limit: Some(5),
    };

    let result = server
        .search_similar_categories(Parameters(input))
        .await;

    assert!(result.is_err());
    let err = result.unwrap_err();
    assert_eq!(err.code, ErrorCode::INVALID_PARAMS);
    assert!(err.message.contains("query must not be empty"));
}

#[tokio::test]
async fn test_server_list_accounts() {
    let db = Arc::new(common::MockDatabase::new());
    let embedder = Arc::new(common::MockEmbedder::new(vec![0.1, 0.2, 0.3]));
    let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

    // Configure mock database to return specific accounts
    db.configure(|state| {
        state.accounts = vec![
            json!({ "id": "acct-1", "name": "Test Account 1", "type": "offchain" }),
            json!({ "id": "acct-2", "name": "Test Account 2", "type": "offchain" }),
        ];
    });

    let input = ListAccountsInput {
        r#type: Some(AccountType::Offchain),
        search: Some("Test".to_string()),
    };

    let result = server
        .list_accounts(Parameters(input.clone()))
        .await
        .expect("tool call should succeed");

    let payload = result.structured_content.expect("structured payload");
    assert_eq!(payload["accounts"].as_array().unwrap().len(), 2);
    assert_eq!(payload["accounts"][0]["id"], "acct-1");
    assert_eq!(payload["accounts"][0]["name"], "Test Account 1");
    assert_eq!(payload["accounts"][0]["type"], "offchain");
    assert_eq!(payload["accounts"][1]["id"], "acct-2");
    assert_eq!(payload["accounts"][1]["name"], "Test Account 2");
    assert_eq!(payload["accounts"][1]["type"], "offchain");

    let list_params = db.account_list_params();
    assert_eq!(list_params.len(), 1);
    assert_eq!(list_params[0].r#type, Some(AccountType::Offchain));
    assert_eq!(list_params[0].search, Some("Test".to_string()));
}

#[tokio::test]
async fn test_server_upsert_account() {
    let db = Arc::new(common::MockDatabase::new());
    let embedder = Arc::new(common::MockEmbedder::new(vec![0.1, 0.2, 0.3]));
    let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

    let input = UpsertAccountInput {
        name: "Checking".to_string(),
        r#type: AccountType::Offchain,
        currency: "USD".to_string(),
        network: None,
        institution: Some("Test Bank".to_string()),
    };

    let result = server
        .upsert_account(Parameters(input.clone()))
        .await
        .expect("tool call should succeed");

    let payload = result.structured_content.expect("structured payload");
    assert_eq!(payload["account"]["id"], "acct-default");

    let upserted = db.upserted_accounts();
    assert_eq!(upserted.len(), 1);
    assert_eq!(upserted[0].name, input.name);
    assert_eq!(upserted[0].r#type, input.r#type);
    assert_eq!(upserted[0].currency, input.currency);
    assert_eq!(upserted[0].network, input.network);
    assert_eq!(upserted[0].institution, input.institution);

    let calls = embedder.calls();
    assert_eq!(calls.len(), 1);
    assert_eq!(calls[0], "Checking");
}

#[tokio::test]
async fn test_server_complete_workflow() {
    let db = Arc::new(common::MockDatabase::new());
    let embedder = Arc::new(common::MockEmbedder::new(vec![0.1, 0.2, 0.3]));
    let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

    // 1. Create an account
    let acct_input = UpsertAccountInput {
        name: "Checking".to_string(),
        r#type: AccountType::Offchain,
        currency: "USD".to_string(),
        network: None,
        institution: Some("Test Bank".to_string()),
    };
    server.upsert_account(Parameters(acct_input)).await.unwrap();

    // 2. Create a category
    let cat_input = UpsertCategoryInput {
        name: "Food".to_string(),
        kind: Some(CategoryKind::Expense),
        description: Some("Food and dining expenses".to_string()),
    };
    server.upsert_category(Parameters(cat_input)).await.unwrap();

    // 3. Create a transaction
    let txn_input = CreateTransactionInput {
        account_id: "acct-1".to_string(),
        amount: 42.0,
        currency: "USD".to_string(),
        direction: TransactionDirection::Expense,
        occurred_at: "2024-01-02T03:04:05Z".to_string(),
        description: Some("Coffee".to_string()),
        raw_source: None,
    };
    server.create_transaction(Parameters(txn_input)).await.unwrap();

    // 4. Search for similar transactions
    let search_input = SearchSimilarInput {
        query: "Coffee".to_string(),
        limit: Some(5),
    };
    server.search_similar_transactions(Parameters(search_input)).await.unwrap();

    // Verify all operations were recorded
    assert_eq!(db.upserted_accounts().len(), 1);
    assert_eq!(db.upserted_categories().len(), 1);
    assert_eq!(db.inserted_transactions().len(), 1);
    assert_eq!(db.transaction_search_limits().len(), 1);

    // Verify embedder calls
    let calls = embedder.calls();
    assert_eq!(calls.len(), 4); // One for account, one for category, one for transaction, one for search
    assert_eq!(calls[0], "Checking"); // Account name is used for embedding
    assert_eq!(calls[1], "Food and dining expenses"); // Description is used for embedding
    assert_eq!(calls[2], "Coffee");
    assert_eq!(calls[3], "Coffee");
}
