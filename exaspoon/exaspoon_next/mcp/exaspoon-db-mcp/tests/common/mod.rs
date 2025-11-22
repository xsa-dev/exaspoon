//! Common test utilities for ExaSpoon MCP server tests.

use anyhow::Result;
use async_trait::async_trait;
use std::sync::{Arc, Mutex};

// Import from the crate using the library name from Cargo.toml
use exaspoon_db_mcp::{
    config::AppConfig,
    embedding::Embedder,
    models::{
        AccountType, CategoryKind, CreateTransactionInput, ListAccountsInput, SearchSimilarInput,
        TransactionDirection, UpsertAccountInput, UpsertCategoryInput,
    },
    supabase::Database,
};
use serde_json::{json, Value};

/// A mock embedder for testing purposes.
#[derive(Clone)]
pub struct MockEmbedder {
    /// The vector to return for all embeddings.
    vector: Vec<f32>,
    /// Tracks calls made to embedder.
    calls: Arc<Mutex<Vec<String>>>,
}

impl MockEmbedder {
    /// Creates a new mock embedder that returns specified vector.
    pub fn new(vector: Vec<f32>) -> Self {
        Self {
            vector,
            calls: Arc::new(Mutex::new(Vec::new())),
        }
    }

    /// Returns a copy of all calls made to embedder.
    pub fn calls(&self) -> Vec<String> {
        self.calls.lock().unwrap().clone()
    }

    /// Clears call history.
    pub fn clear_calls(&self) {
        self.calls.lock().unwrap().clear();
    }
}

#[async_trait]
impl Embedder for MockEmbedder {
    async fn embed(&self, text: &str) -> Result<Vec<f32>> {
        self.calls.lock().unwrap().push(text.to_string());
        Ok(self.vector.clone())
    }

    async fn maybe_embed(&self, text: Option<&str>) -> Result<Option<Vec<f32>>> {
        match text {
            Some(value) => Ok(Some(self.embed(value).await?)),
            None => Ok(None),
        }
    }
}

/// A mock database for testing purposes.
#[derive(Clone)]
pub struct MockDatabase {
    /// Internal state of mock database.
    state: Arc<Mutex<MockState>>,
}

impl MockDatabase {
    /// Creates a new mock database with default state.
    pub fn new() -> Self {
        Self {
            state: Arc::new(Mutex::new(MockState::default())),
        }
    }

    /// Configures mock database with custom state.
    pub fn configure<F>(&self, mutate: F)
    where
        F: FnOnce(&mut MockState),
    {
        let mut state = self.state.lock().unwrap();
        mutate(&mut state);
    }

    /// Returns all inserted transactions.
    pub fn inserted_transactions(&self) -> Vec<(CreateTransactionInput, Option<Vec<f32>>)> {
        self.state.lock().unwrap().inserted_transactions.clone()
    }

    /// Returns all transaction search limits.
    pub fn transaction_search_limits(&self) -> Vec<Option<u32>> {
        self.state.lock().unwrap().searched_transaction_limits.clone()
    }

    /// Returns all upserted categories.
    pub fn upserted_categories(&self) -> Vec<(UpsertCategoryInput, Option<Vec<f32>>)> {
        self.state.lock().unwrap().upserted_categories.clone()
    }

    /// Returns all upserted accounts.
    pub fn upserted_accounts(&self) -> Vec<UpsertAccountInput> {
        self.state.lock().unwrap().upserted_accounts.clone()
    }

    /// Returns all account list parameters.
    pub fn account_list_params(&self) -> Vec<ListAccountsInput> {
        self.state.lock().unwrap().account_list_params.clone()
    }
}

#[async_trait]
impl Database for MockDatabase {
    async fn insert_transaction(
        &self,
        input: &CreateTransactionInput,
        embedding: Option<Vec<f32>>,
    ) -> Result<Value> {
        let mut state = self.state.lock().unwrap();
        state.inserted_transactions.push((input.clone(), embedding));
        Ok(state.transaction_response.clone())
    }

    async fn upsert_category(
        &self,
        input: &UpsertCategoryInput,
        embedding: Option<Vec<f32>>,
    ) -> Result<Value> {
        let mut state = self.state.lock().unwrap();
        state.upserted_categories.push((input.clone(), embedding));
        Ok(state.category_response.clone())
    }

    async fn upsert_account(&self, input: &UpsertAccountInput) -> Result<Value> {
        let mut state = self.state.lock().unwrap();
        state.upserted_accounts.push(input.clone());
        Ok(state.account_response.clone())
    }

    async fn list_accounts(&self, params: &ListAccountsInput) -> Result<Vec<Value>> {
        let mut state = self.state.lock().unwrap();
        state.account_list_params.push(params.clone());
        Ok(state.accounts.clone())
    }

    async fn search_similar_transactions(
        &self,
        embedding: Vec<f32>,
        limit: Option<u32>,
    ) -> Result<Vec<Value>> {
        let mut state = self.state.lock().unwrap();
        state.searched_transaction_limits.push(limit);
        Ok(state.transaction_matches.clone())
    }

    async fn search_similar_categories(
        &self,
        embedding: Vec<f32>,
        _limit: Option<u32>,
    ) -> Result<Vec<Value>> {
        let state = self.state.lock().unwrap();
        Ok(state.category_matches.clone())
    }
}

/// Internal state for mock database.
#[derive(Clone)]
pub struct MockState {
    /// All inserted transactions.
    pub inserted_transactions: Vec<(CreateTransactionInput, Option<Vec<f32>>)>,
    /// All transaction search limits.
    pub searched_transaction_limits: Vec<Option<u32>>,
    /// Default transaction response.
    pub transaction_response: Value,
    /// Transaction search matches.
    pub transaction_matches: Vec<Value>,
    /// All upserted categories.
    pub upserted_categories: Vec<(UpsertCategoryInput, Option<Vec<f32>>)>,
    /// Default category response.
    pub category_response: Value,
    /// Category search matches.
    pub category_matches: Vec<Value>,
    /// All upserted accounts.
    pub upserted_accounts: Vec<UpsertAccountInput>,
    /// Default account response.
    pub account_response: Value,
    /// Account list results.
    pub accounts: Vec<Value>,
    /// All account list parameters.
    pub account_list_params: Vec<ListAccountsInput>,
}

impl Default for MockState {
    fn default() -> Self {
        Self {
            inserted_transactions: Vec::new(),
            searched_transaction_limits: Vec::new(),
            transaction_response: json!({ "id": "txn-default" }),
            transaction_matches: Vec::new(),
            upserted_categories: Vec::new(),
            category_response: json!({ "id": "cat-default" }),
            category_matches: Vec::new(),
            upserted_accounts: Vec::new(),
            account_response: json!({ "id": "acct-default" }),
            accounts: Vec::new(),
            account_list_params: Vec::new(),
        }
    }
}

/// Creates a test configuration with mock values.
pub fn test_config() -> AppConfig {
    AppConfig {
        supabase_url: "https://test.supabase.co".to_string(),
        supabase_service_key: "test-service-key".to_string(),
        openai_api_key: "test-openai-key".to_string(),
        openai_base_url: Some("https://test.openai.com".to_string()),
        embedding_model: "text-embedding-3-large".to_string(),
    }
}

/// Creates a sample transaction input for testing.
pub fn sample_transaction_input() -> CreateTransactionInput {
    CreateTransactionInput {
        account_id: "acct-1".to_string(),
        amount: 42.0,
        currency: "USD".to_string(),
        direction: TransactionDirection::Expense,
        occurred_at: "2024-01-02T03:04:05Z".to_string(),
        description: Some("Coffee".to_string()),
        raw_source: None,
    }
}

/// Creates a sample category input for testing.
pub fn sample_category_input() -> UpsertCategoryInput {
    UpsertCategoryInput {
        name: "Food".to_string(),
        kind: Some(CategoryKind::Expense),
        description: Some("Food and dining expenses".to_string()),
    }
}

/// Creates a sample account input for testing.
pub fn sample_account_input() -> UpsertAccountInput {
    UpsertAccountInput {
        name: "Checking".to_string(),
        r#type: AccountType::Offchain,
        currency: "USD".to_string(),
        network: None,
        institution: Some("Test Bank".to_string()),
    }
}

/// Creates a sample search input for testing.
pub fn sample_search_input() -> SearchSimilarInput {
    SearchSimilarInput {
        query: "Coffee shop".to_string(),
        limit: Some(5),
    }
}
