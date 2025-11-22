use crate::{
    embedding::Embedder,
    models::{
        CreateTransactionInput, ListAccountsInput, SearchSimilarInput, UpsertAccountInput,
        UpsertCategoryInput,
    },
    supabase::Database,
};
use rmcp::{
    handler::server::{router::tool::ToolRouter, wrapper::Parameters},
    model::{CallToolResult, Implementation, ProtocolVersion, ServerCapabilities, ServerInfo},
    tool, tool_handler, tool_router, ErrorData as McpError, ServerHandler,
};
use serde_json::{json, Value};
use std::sync::Arc;
use std::time::Instant;
use tracing::{debug, error, info, instrument, warn};

#[derive(Clone)]
pub struct ExaspoonDbServer {
    supabase: Arc<dyn Database>,
    embedder: Arc<dyn Embedder>,
    tool_router: ToolRouter<Self>,
}

#[tool_router]
impl ExaspoonDbServer {
    pub fn new(supabase: Arc<dyn Database>, embedder: Arc<dyn Embedder>) -> Self {
        Self {
            supabase,
            embedder,
            tool_router: Self::tool_router(),
        }
    }

    #[tool(description = "Insert a transaction row, automatically embedding the description.")]
    #[instrument(skip(self), fields(account_id = %input.account_id, amount = %input.amount, currency = %input.currency))]
    pub async fn create_transaction(
        &self,
        Parameters(input): Parameters<CreateTransactionInput>,
    ) -> Result<CallToolResult, McpError> {
        let start_time = Instant::now();
        info!("Creating transaction for account: {}", input.account_id);
        
        let embedding = self
            .embedder
            .maybe_embed(input.description.as_deref())
            .await
            .map_err(|err| {
                error!("Failed to generate transaction embedding: {}", err);
                internal_error("generate transaction embedding", err)
            })?;

        let record = self
            .supabase
            .insert_transaction(&input, embedding)
            .await
            .map_err(|err| {
                error!("Failed to insert transaction: {}", err);
                internal_error("insert transaction", err)
            })?;

        let duration = start_time.elapsed();
        info!("Transaction created successfully in {:?}", duration);
        debug!("Transaction record: {:?}", record);
        
        Ok(success(json!({ "transaction": record })))
    }

    #[tool(description = "Semantic nearest-neighbor search over historical transactions.")]
    #[instrument(skip(self), fields(query = %input.query, limit = ?input.limit))]
    pub async fn search_similar_transactions(
        &self,
        Parameters(input): Parameters<SearchSimilarInput>,
    ) -> Result<CallToolResult, McpError> {
        let start_time = Instant::now();
        info!("Searching for similar transactions with query: {}", input.query);
        
        if input.query.trim().is_empty() {
            warn!("Empty query provided for transaction search");
            return Err(McpError::invalid_params(
                "query must not be empty",
                Some(json!({ "field": "query" })),
            ));
        }

        let embedding = self
            .embedder
            .embed(input.query.trim())
            .await
            .map_err(|err| {
                error!("Failed to embed query text: {}", err);
                internal_error("embed query text", err)
            })?;

        let matches = self
            .supabase
            .search_similar_transactions(embedding, input.limit)
            .await
            .map_err(|err| {
                error!("Failed to search similar transactions: {}", err);
                internal_error("search similar transactions", err)
            })?;

        let duration = start_time.elapsed();
        info!("Found {} similar transactions in {:?}", matches.len(), duration);
        debug!("Transaction matches: {:?}", matches);

        Ok(success(json!({ "matches": matches })))
    }

    #[tool(description = "Create or update a category with embeddings for semantic search.")]
    #[instrument(skip(self), fields(category_name = %input.name, kind = ?input.kind))]
    pub async fn upsert_category(
        &self,
        Parameters(input): Parameters<UpsertCategoryInput>,
    ) -> Result<CallToolResult, McpError> {
        let start_time = Instant::now();
        info!("Upserting category: {}", input.name);
        
        let description_source = input.description.as_deref().unwrap_or(input.name.as_str());
        let embedding = self
            .embedder
            .embed(description_source)
            .await
            .map_err(|err| {
                error!("Failed to generate category embedding: {}", err);
                internal_error("generate category embedding", err)
            })?;

        let category = self
            .supabase
            .upsert_category(&input, Some(embedding))
            .await
            .map_err(|err| {
                error!("Failed to upsert category: {}", err);
                internal_error("upsert category", err)
            })?;

        let duration = start_time.elapsed();
        info!("Category upserted successfully in {:?}", duration);
        debug!("Category record: {:?}", category);

        Ok(success(json!({ "category": category })))
    }

    #[tool(description = "Semantic search across categories by embedding query.")]
    #[instrument(skip(self), fields(query = %input.query, limit = ?input.limit))]
    pub async fn search_similar_categories(
        &self,
        Parameters(input): Parameters<SearchSimilarInput>,
    ) -> Result<CallToolResult, McpError> {
        let start_time = Instant::now();
        info!("Searching for similar categories with query: {}", input.query);
        
        if input.query.trim().is_empty() {
            warn!("Empty query provided for category search");
            return Err(McpError::invalid_params(
                "query must not be empty",
                Some(json!({ "field": "query" })),
            ));
        }

        let embedding = self
            .embedder
            .embed(input.query.trim())
            .await
            .map_err(|err| {
                error!("Failed to embed query text: {}", err);
                internal_error("embed query text", err)
            })?;

        let matches = self
            .supabase
            .search_similar_categories(embedding, input.limit)
            .await
            .map_err(|err| {
                error!("Failed to search similar categories: {}", err);
                internal_error("search similar categories", err)
            })?;

        let duration = start_time.elapsed();
        info!("Found {} similar categories in {:?}", matches.len(), duration);
        debug!("Category matches: {:?}", matches);

        Ok(success(json!({ "matches": matches })))
    }

    #[tool(description = "List accounts with optional filters by type or name substring.")]
    #[instrument(skip(self), fields(account_type = ?input.r#type, search = ?input.search))]
    pub async fn list_accounts(
        &self,
        Parameters(input): Parameters<ListAccountsInput>,
    ) -> Result<CallToolResult, McpError> {
        let start_time = Instant::now();
        info!("Listing accounts with filters: type={:?}, search={:?}", input.r#type, input.search);
        
        let accounts = self
            .supabase
            .list_accounts(&input)
            .await
            .map_err(|err| {
                error!("Failed to list accounts: {}", err);
                internal_error("list accounts", err)
            })?;

        let duration = start_time.elapsed();
        info!("Found {} accounts in {:?}", accounts.len(), duration);
        debug!("Account list: {:?}", accounts);

        Ok(success(json!({ "accounts": accounts })))
    }

    #[tool(description = "Create or update an account keyed by name+type.")]
    #[instrument(skip(self), fields(account_name = %input.name, account_type = %input.r#type, currency = %input.currency))]
    pub async fn upsert_account(
        &self,
        Parameters(input): Parameters<UpsertAccountInput>,
    ) -> Result<CallToolResult, McpError> {
        let start_time = Instant::now();
        info!("Upserting account: {} ({})", input.name, input.r#type);
        
        let _embedding = self
            .embedder
            .embed(&input.name)
            .await
            .map_err(|err| {
                error!("Failed to generate account embedding: {}", err);
                internal_error("generate account embedding", err)
            })?;

        let account = self
            .supabase
            .upsert_account(&input)
            .await
            .map_err(|err| {
                error!("Failed to upsert account: {}", err);
                internal_error("upsert account", err)
            })?;

        let duration = start_time.elapsed();
        info!("Account upserted successfully in {:?}", duration);
        debug!("Account record: {:?}", account);

        Ok(success(json!({ "account": account })))
    }
}

#[tool_handler]
impl ServerHandler for ExaspoonDbServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo {
            protocol_version: ProtocolVersion::V_2024_11_05,
            capabilities: ServerCapabilities::builder().enable_tools().build(),
            server_info: Implementation::from_build_env(),
            instructions: Some(
                "Tools for managing accounts, transactions, and semantic search over Supabase data."
                    .to_string(),
            ),
        }
    }
}

fn internal_error(action: &str, err: anyhow::Error) -> McpError {
    McpError::internal_error(
        format!("Failed to {action}"),
        Some(json!({ "details": err.to_string() })),
    )
}

fn success(value: Value) -> CallToolResult {
    CallToolResult::structured(value)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::{
        CreateTransactionInput, ListAccountsInput, SearchSimilarInput, TransactionDirection,
        UpsertAccountInput, UpsertCategoryInput,
    };
    use crate::{embedding::Embedder, supabase::Database};
    use anyhow::Result;
    use async_trait::async_trait;
    use rmcp::model::ErrorCode;
    use serde_json::{json, Value};
    use std::sync::Mutex;

    #[tokio::test]
    async fn rejects_blank_transaction_query() {
        let db = Arc::new(FakeDatabase::default());
        let embedder = Arc::new(FakeEmbedder::new(vec![0.1]));
        let server = ExaspoonDbServer::new(db, embedder);

        let err = server
            .search_similar_transactions(Parameters(SearchSimilarInput {
                query: "   ".into(),
                limit: None,
            }))
            .await
            .expect_err("expected validation error");

        assert_eq!(err.code, ErrorCode::INVALID_PARAMS);
    }

    #[tokio::test]
    async fn search_similar_transactions_returns_matches() {
        let db = Arc::new(FakeDatabase::default());
        db.configure(|state| {
            state.transaction_matches = vec![json!({"id": "txn-42"})];
        });
        let embedder = Arc::new(FakeEmbedder::new(vec![0.2, 0.4]));
        let server = ExaspoonDbServer::new(db.clone(), embedder.clone());

        let result = server
            .search_similar_transactions(Parameters(SearchSimilarInput {
                query: "Rent".into(),
                limit: Some(7),
            }))
            .await
            .expect("tool call should succeed");

        let payload = result.structured_content.expect("structured payload");
        assert_eq!(payload["matches"][0]["id"], "txn-42");
        assert_eq!(embedder.calls(), vec!["Rent"]);
        assert_eq!(db.transaction_search_limits(), vec![Some(7)]);
    }

    #[tokio::test]
    async fn create_transaction_embeds_description() {
        let db = Arc::new(FakeDatabase::default());
        let embedder = Arc::new(FakeEmbedder::new(vec![0.5]));
        let server = ExaspoonDbServer::new(db.clone(), embedder.clone());
        let input = CreateTransactionInput {
            account_id: "acct-1".into(),
            amount: 42.0,
            currency: "USD".into(),
            direction: TransactionDirection::Expense,
            occurred_at: "2024-01-02T03:04:05Z".into(),
            description: Some("Coffee".into()),
            raw_source: None,
        };

        let _ = server
            .create_transaction(Parameters(input.clone()))
            .await
            .expect("tool call should succeed");

        let inserts = db.inserted_transactions();
        assert_eq!(inserts.len(), 1);
        assert_eq!(inserts[0].0.description.as_deref(), Some("Coffee"));
        assert_eq!(inserts[0].1, Some(vec![0.5]));
        assert_eq!(embedder.calls(), vec!["Coffee"]);
    }

    #[tokio::test]
    async fn create_transaction_skips_embedding_without_description() {
        let db = Arc::new(FakeDatabase::default());
        let embedder = Arc::new(FakeEmbedder::new(vec![0.9]));
        let server = ExaspoonDbServer::new(db.clone(), embedder.clone());
        let input = CreateTransactionInput {
            account_id: "acct-2".into(),
            amount: 10.0,
            currency: "USD".into(),
            direction: TransactionDirection::Income,
            occurred_at: "2024-01-02T03:04:05Z".into(),
            description: None,
            raw_source: None,
        };

        server
            .create_transaction(Parameters(input))
            .await
            .expect("tool call should succeed");

        let inserts = db.inserted_transactions();
        assert_eq!(inserts[0].1, None);
        assert!(embedder.calls().is_empty());
    }

    #[derive(Default)]
    struct FakeEmbedder {
        vector: Vec<f32>,
        calls: Mutex<Vec<String>>,
    }

    impl FakeEmbedder {
        fn new(vector: Vec<f32>) -> Self {
            Self {
                vector,
                calls: Mutex::new(Vec::new()),
            }
        }

        fn calls(&self) -> Vec<String> {
            self.calls.lock().unwrap().clone()
        }
    }

    #[async_trait]
    impl Embedder for FakeEmbedder {
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

    #[derive(Default)]
    struct FakeDatabase {
        state: Mutex<FakeState>,
    }

    impl FakeDatabase {
        fn configure<F>(&self, mutate: F)
        where
            F: FnOnce(&mut FakeState),
        {
            let mut state = self.state.lock().unwrap();
            mutate(&mut state);
        }

        fn inserted_transactions(&self) -> Vec<(CreateTransactionInput, Option<Vec<f32>>)> {
            self.state.lock().unwrap().inserted_transactions.clone()
        }

        fn transaction_search_limits(&self) -> Vec<Option<u32>> {
            self.state
                .lock()
                .unwrap()
                .searched_transaction_limits
                .clone()
        }
    }

    #[derive(Clone)]
    struct FakeState {
        inserted_transactions: Vec<(CreateTransactionInput, Option<Vec<f32>>)>,
        searched_transaction_limits: Vec<Option<u32>>,
        transaction_response: Value,
        transaction_matches: Vec<Value>,
        category_response: Value,
        category_matches: Vec<Value>,
        accounts: Vec<Value>,
        account_response: Value,
    }

    impl Default for FakeState {
        fn default() -> Self {
            Self {
                inserted_transactions: Vec::new(),
                searched_transaction_limits: Vec::new(),
                transaction_response: json!({ "id": "txn-default" }),
                transaction_matches: Vec::new(),
                category_response: json!({ "id": "cat-default" }),
                category_matches: Vec::new(),
                accounts: Vec::new(),
                account_response: json!({ "id": "acct-default" }),
            }
        }
    }

    #[async_trait]
    impl Database for FakeDatabase {
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
            _input: &UpsertCategoryInput,
            _embedding: Option<Vec<f32>>,
        ) -> Result<Value> {
            let state = self.state.lock().unwrap();
            Ok(state.category_response.clone())
        }

        async fn upsert_account(&self, _input: &UpsertAccountInput) -> Result<Value> {
            let state = self.state.lock().unwrap();
            Ok(state.account_response.clone())
        }

        async fn list_accounts(&self, _params: &ListAccountsInput) -> Result<Vec<Value>> {
            let state = self.state.lock().unwrap();
            Ok(state.accounts.clone())
        }

        async fn search_similar_transactions(
            &self,
            _embedding: Vec<f32>,
            limit: Option<u32>,
        ) -> Result<Vec<Value>> {
            let mut state = self.state.lock().unwrap();
            state.searched_transaction_limits.push(limit);
            Ok(state.transaction_matches.clone())
        }

        async fn search_similar_categories(
            &self,
            _embedding: Vec<f32>,
            _limit: Option<u32>,
        ) -> Result<Vec<Value>> {
            let state = self.state.lock().unwrap();
            Ok(state.category_matches.clone())
        }
    }
}
