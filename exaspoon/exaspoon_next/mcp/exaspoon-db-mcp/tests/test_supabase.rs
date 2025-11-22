//! Tests for database operations.

use exaspoon_db_mcp::embedding::Embedder;
use exaspoon_db_mcp::models::{
    AccountType, CategoryKind, CreateTransactionInput, ListAccountsInput, SearchSimilarInput,
    TransactionDirection, UpsertAccountInput, UpsertCategoryInput,
};
use exaspoon_db_mcp::supabase::Database;
use serde_json::json;

mod common;

#[tokio::test]
async fn test_mock_database_insert_transaction() {
    let db = common::MockDatabase::new();
    let input = common::sample_transaction_input();
    let embedding = Some(vec![0.1, 0.2, 0.3]);

    let result = db.insert_transaction(
        &input,
        Some(vec![0.1, 0.2, 0.3]),
    )
    .await
    .unwrap();
    assert_eq!(result, json!({ "id": "txn-default" }));

    let inserted = db.inserted_transactions();
    assert_eq!(inserted.len(), 1);
    assert_eq!(inserted[0].0.account_id, input.account_id);
    assert_eq!(inserted[0].1, embedding);
}

#[tokio::test]
async fn test_mock_database_upsert_category() {
    let db = common::MockDatabase::new();
    let input = common::sample_category_input();
    let embedding = Some(vec![0.4, 0.5, 0.6]);

    let result = db.upsert_category(
        &input,
        Some(vec![0.4, 0.5, 0.6]),
    )
    .await
    .unwrap();
    assert_eq!(result, json!({ "id": "cat-default" }));

    let upserted = db.upserted_categories();
    assert_eq!(upserted.len(), 1);
    assert_eq!(upserted[0].0.name, input.name);
    assert_eq!(upserted[0].0.kind, input.kind);
    assert_eq!(upserted[0].0.description, input.description);
    assert_eq!(upserted[0].1, embedding);
}

#[tokio::test]
async fn test_mock_database_upsert_account() {
    let db = common::MockDatabase::new();
    let input = common::sample_account_input();

    let result = db.upsert_account(
        &input,
    )
    .await
    .unwrap();
    assert_eq!(result, json!({ "id": "acct-default" }));

    let upserted = db.upserted_accounts();
    assert_eq!(upserted.len(), 1);
    assert_eq!(upserted[0].name, input.name);
    assert_eq!(upserted[0].r#type, input.r#type);
    assert_eq!(upserted[0].currency, input.currency);
    assert_eq!(upserted[0].network, input.network);
    assert_eq!(upserted[0].institution, input.institution);
}

#[tokio::test]
async fn test_mock_database_list_accounts() {
    let db = common::MockDatabase::new();
    let params = exaspoon_db_mcp::models::ListAccountsInput {
        r#type: Some(AccountType::Offchain),
        search: Some("Test".to_string()),
    };

    let result = db.list_accounts(
        &params
    )
    .await
    .unwrap();
    assert_eq!(result, vec![
        json!({ "id": "acct-1", "name": "Test Account 1" }),
        json!({ "id": "acct-2", "name": "Test Account 2" }),
    ]);

    let list_params = db.account_list_params();
    assert_eq!(list_params.len(), 1);
    assert_eq!(list_params[0].r#type, Some(AccountType::Offchain));
    assert_eq!(list_params[0].search, Some("Test".to_string()));
}

#[tokio::test]
async fn test_mock_database_search_similar_transactions() {
    let db = common::MockDatabase::new();
    let embedding = vec![0.7, 0.8, 0.9];
    let limit = Some(10);

    // Configure mock database to return specific matches
    db.configure(|state| {
        state.transaction_matches = vec![
            json!({ "id": "txn-1", "description": "Coffee shop" }),
            json!({ "id": "txn-2", "description": "Cafe" }),
        ];
    });

    let result = db.search_similar_transactions(
        embedding.clone(), limit.clone()
    )
    .await
    .unwrap();
    assert_eq!(result, vec![
        json!({ "id": "txn-1", "description": "Coffee shop" }),
        json!({ "id": "txn-2", "description": "Cafe" }),
    ]);

    let search_limits = db.transaction_search_limits();
    assert_eq!(search_limits.len(), 1);
    assert_eq!(search_limits[0], Some(10));
}

#[tokio::test]
async fn test_mock_database_search_similar_categories() {
    let db = common::MockDatabase::new();
    let embedding = vec![0.4, 0.8, 0.12];

    // Configure mock database to return specific matches
    db.configure(|state| {
        state.category_matches = vec![
            json!({ "id": "cat-1", "name": "Food" }),
            json!({ "id": "cat-2", "name": "Dining" }),
        ];
    });

    let result = db.search_similar_categories(
        embedding.clone(), None
    )
    .await
    .unwrap();
    assert_eq!(result, vec![
        json!({ "id": "cat-1", "name": "Food" }),
        json!({ "id": "cat-2", "name": "Dining" }),
        ]);
}

#[tokio::test]
async fn test_mock_database_multiple_operations() {
    let db = common::MockDatabase::new();
    let embedder = common::MockEmbedder::new(vec![0.1, 0.2, 0.3]);

    // Insert transaction
    let txn_input = common::sample_transaction_input();
    db.insert_transaction(&txn_input, Some(vec![0.1, 0.2, 0.3])).await.unwrap();

    // Upsert category
    let cat_input = common::sample_category_input();
    db.upsert_category(&cat_input, Some(vec![0.4, 0.5, 0.6])).await.unwrap();

    // Upsert account
    let acct_input = common::sample_account_input();
    db.upsert_account(&acct_input).await.unwrap();

    // Search for similar transactions
    let search_input = exaspoon_db_mcp::models::SearchSimilarInput {
        query: "Coffee".to_string(),
        limit: Some(5),
    };
    let embedding = embedder.embed(&search_input.query).await.unwrap();
    db.search_similar_transactions(embedding, search_input.limit).await.unwrap();

    // Verify all operations were recorded
    assert_eq!(db.inserted_transactions().len(), 1);
    assert_eq!(db.upserted_categories().len(), 1);
    assert_eq!(db.upserted_accounts().len(), 1);
    assert_eq!(db.transaction_search_limits().len(), 1);

    // Verify embedder calls
    let calls = embedder.calls();
    assert_eq!(calls.len(), 3);
    assert_eq!(calls[0], "Food and dining expenses"); // Category description
    assert_eq!(calls[1], "Coffee"); // Transaction description
    assert_eq!(calls[2], "Coffee"); // Search query
}

#[tokio::test]
async fn test_mock_database_configure_custom_state() {
    let db = common::MockDatabase::new();

    // Configure custom state
    db.configure(|state| {
        state.transaction_response = json!({ "id": "custom-txn" });
        state.category_response = json!({ "id": "custom-cat" });
        state.account_response = json!({ "id": "custom-acct" });
        state.accounts = vec![
            json!({ "id": "acct-1", "name": "Custom Account 1" }),
            json!({ "id": "acct-2", "name": "Custom Account 2" }),
        ];
        state.transaction_matches = vec![
            json!({ "id": "txn-1", "description": "Custom Transaction" }),
            json!({ "id": "txn-2", "description": "Custom Transaction" }),
        ];
        state.category_matches = vec![
            json!({ "id": "cat-1", "name": "Custom Category" }),
            json!({ "id": "cat-2", "name": "Custom Category" }),
        ];
    });

    // Test that custom responses are returned
    let txn_input = common::sample_transaction_input();
    let txn_result = db.insert_transaction(
        &txn_input, None
    )
    .await
    .unwrap();
    assert_eq!(txn_result, json!({ "id": "custom-txn" }));

    let cat_input = common::sample_category_input();
    let cat_result = db.upsert_category(
        &cat_input, None
    )
    .await
    .unwrap();
    assert_eq!(cat_result, json!({ "id": "custom-cat" }));

    let acct_input = common::sample_account_input();
    let acct_result = db.upsert_account(
        &acct_input
    )
    .await
    .unwrap();
    assert_eq!(acct_result, json!({ "id": "custom-acct" }));

    let list_result = db.list_accounts(
        &exaspoon_db_mcp::models::ListAccountsInput::default()
    )
    .await
    .unwrap();
    assert_eq!(list_result, vec![
        json!({ "id": "acct-1", "name": "Custom Account" }),
        json!({ "id": "acct-2", "name": "Custom Account 2" }),
        ]);

    let search_result = db.search_similar_transactions(
        vec![0.1, 0.2, 0.3], None
    )
    .await
    .unwrap();
    assert_eq!(search_result, vec![
        json!({ "id": "txn-1", "description": "Custom Transaction" })
    ]);
}
