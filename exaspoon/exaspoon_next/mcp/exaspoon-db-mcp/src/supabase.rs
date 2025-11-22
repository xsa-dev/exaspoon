use crate::{
    config::AppConfig,
    models::{
        AccountType, CategoryKind, CreateTransactionInput, ListAccountsInput, UpsertAccountInput,
        UpsertCategoryInput,
    },
};
use anyhow::{anyhow, Context, Result};
use async_trait::async_trait;
use reqwest::{
    header::{HeaderMap, HeaderValue, ACCEPT, AUTHORIZATION, CONTENT_TYPE},
    Client,
};
use serde_json::{json, Value};
use std::time::Instant;
use supabase_rs::SupabaseClient;
use tracing::{debug, error, info, instrument, warn};

#[async_trait]
pub trait Database: Send + Sync {
    async fn insert_transaction(
        &self,
        input: &CreateTransactionInput,
        embedding: Option<Vec<f32>>,
    ) -> Result<Value>;
    async fn upsert_category(
        &self,
        input: &UpsertCategoryInput,
        embedding: Option<Vec<f32>>,
    ) -> Result<Value>;
    async fn upsert_account(&self, input: &UpsertAccountInput) -> Result<Value>;
    async fn list_accounts(&self, params: &ListAccountsInput) -> Result<Vec<Value>>;
    async fn search_similar_transactions(
        &self,
        embedding: Vec<f32>,
        limit: Option<u32>,
    ) -> Result<Vec<Value>>;
    async fn search_similar_categories(
        &self,
        embedding: Vec<f32>,
        limit: Option<u32>,
    ) -> Result<Vec<Value>>;
}

#[derive(Clone)]
pub struct SupabaseGateway {
    client: SupabaseClient,
    http: Client,
    _rest_base: String,
    rpc_base: String,
    service_key: String,
    schema: String,
}

impl SupabaseGateway {
    #[instrument]
    pub fn new(config: &AppConfig) -> Result<Self> {
        info!("Initializing Supabase gateway");
        debug!("Supabase URL: {}", config.supabase_url);
        
        let client = SupabaseClient::new(
            config.supabase_url.clone(),
            config.supabase_service_key.clone(),
        )
        .map_err(|err| {
            error!("Failed to initialize Supabase client: {}", err);
            anyhow!("failed to initialize Supabase client: {err}")
        })?;

        let use_native_tls = std::env::var("USE_NATIVE_TLS")
            .map(|value| value.eq_ignore_ascii_case("true"))
            .unwrap_or(false);
        
        let tls_min_version = std::env::var("TLS_MIN_VERSION")
            .unwrap_or_else(|_| "1.2".to_string());
        
        let danger_accept_invalid_certs = std::env::var("DANGER_ACCEPT_INVALID_CERTS")
            .map(|value| value.eq_ignore_ascii_case("true"))
            .unwrap_or(false);
        
        info!("Using TLS backend: {}", if use_native_tls { "native" } else { "rustls" });
        info!("TLS min version: {}", tls_min_version);
        if danger_accept_invalid_certs {
            warn!("WARNING: TLS certificate verification disabled - FOR TESTING ONLY");
        }
        
        let http = if use_native_tls {
            let mut builder = Client::builder().use_native_tls();
            if danger_accept_invalid_certs {
                builder = builder.danger_accept_invalid_certs(true);
            }
            builder.build()
                .context("failed to build HTTP client with native TLS")?
        } else {
            let mut builder = Client::builder().use_rustls_tls();
            if danger_accept_invalid_certs {
                builder = builder.danger_accept_invalid_certs(true);
            }
            builder.build()
                .context("failed to build HTTP client with rustls")?
        };
        
        let base = config.supabase_url.trim_end_matches('/');
        let use_plain_base = std::env::var("SUPABASE_RS_DONT_REST_V1_URL")
            .map(|value| value.eq_ignore_ascii_case("true"))
            .unwrap_or(false);
        let rest_base = if use_plain_base {
            base.to_string()
        } else {
            format!("{}/rest/v1", base)
        };

        info!("Supabase gateway initialized successfully");
        Ok(Self {
            client,
            http,
            rpc_base: format!("{}/rpc", rest_base),
            _rest_base: rest_base,
            service_key: config.supabase_service_key.clone(),
            schema: "public".to_string(),
        })
    }
}

#[async_trait]
impl Database for SupabaseGateway {
    #[instrument(skip(self, input), fields(account_id = %input.account_id, amount = %input.amount))]
    async fn insert_transaction(
        &self,
        input: &CreateTransactionInput,
        embedding: Option<Vec<f32>>,
    ) -> Result<Value> {
        let start_time = Instant::now();
        info!("Inserting transaction into database");
        
        let payload = json!({
            "account_id": &input.account_id,
            "amount": input.amount,
            "currency": &input.currency,
            "direction": input.direction.as_ref(),
            "occurred_at": &input.occurred_at,
            "description": input.description.clone(),
            "raw_source": input.raw_source.clone(),
            "embedding": embedding,
        });

        let result = self.insert_and_fetch("transactions", payload).await?;
        let duration = start_time.elapsed();
        info!("Transaction inserted successfully in {:?}", duration);
        
        Ok(result)
    }

    #[instrument(skip(self, input), fields(category_name = %input.name, kind = ?input.kind))]
    async fn upsert_category(
        &self,
        input: &UpsertCategoryInput,
        embedding: Option<Vec<f32>>,
    ) -> Result<Value> {
        let start_time = Instant::now();
        info!("Upserting category in database");
        
        let description = input
            .description
            .clone()
            .unwrap_or_else(|| input.name.clone());
        let payload = json!({
            "name": &input.name,
            "kind": input.kind.unwrap_or(CategoryKind::Expense).as_ref(),
            "description": description,
            "embedding": embedding,
        });

        let result = if let Some(existing) = self
            .fetch_first("categories", &[("name", input.name.as_str())])
            .await?
        {
            debug!("Updating existing category");
            let id = self.extract_id(&existing)?;
            self.client
                .update("categories", &id, payload)
                .await
                .map_err(|err| {
                    error!("Failed to update category: {}", err);
                    anyhow!("failed to update category: {err}")
                })?;
            self.fetch_by_id("categories", &id).await?
        } else {
            debug!("Creating new category");
            self.insert_and_fetch("categories", payload).await?
        };
        
        let duration = start_time.elapsed();
        info!("Category upserted successfully in {:?}", duration);
        
        Ok(result)
    }

    #[instrument(skip(self, input), fields(account_name = %input.name, account_type = %input.r#type))]
    async fn upsert_account(&self, input: &UpsertAccountInput) -> Result<Value> {
        let start_time = Instant::now();
        info!("Upserting account in database");
        
        let payload = json!({
            "name": &input.name,
            "type": input.r#type.as_ref(),
            "currency": &input.currency,
            "network": input.network.clone(),
            "institution": input.institution.clone(),
        });

        let result = if let Some(existing) = self.fetch_account(&input.name, input.r#type).await? {
            debug!("Updating existing account");
            let id = self.extract_id(&existing)?;
            self.client
                .update("accounts", &id, payload)
                .await
                .map_err(|err| {
                    error!("Failed to update account: {}", err);
                    anyhow!("failed to update account: {err}")
                })?;
            self.fetch_by_id("accounts", &id).await?
        } else {
            debug!("Creating new account");
            self.insert_and_fetch("accounts", payload).await?
        };
        
        let duration = start_time.elapsed();
        info!("Account upserted successfully in {:?}", duration);
        
        Ok(result)
    }

    #[instrument(skip(self, params), fields(account_type = ?params.r#type, search = ?params.search))]
    async fn list_accounts(&self, params: &ListAccountsInput) -> Result<Vec<Value>> {
        let start_time = Instant::now();
        info!("Listing accounts from database");
        
        let mut query = self.client.select("accounts").order("name", true);
        if let Some(kind) = params.r#type {
            query = query.eq("type", kind.as_ref());
        }

        let rows = query
            .execute()
            .await
            .map_err(|err| {
                error!("Failed to list accounts: {}", err);
                anyhow!("failed to list accounts: {err}")
            })?;

        let result = if let Some(needle) = params
            .search
            .as_ref()
            .map(|value| value.trim())
            .filter(|value| !value.is_empty())
            .map(|value| value.to_lowercase())
        {
            debug!("Filtering accounts by search term: {}", needle);
            rows.into_iter()
                .filter(|row| {
                    row.get("name")
                        .and_then(Value::as_str)
                        .map(|value| value.to_lowercase().contains(&needle))
                        .unwrap_or(false)
                })
                .collect::<Vec<_>>()
        } else {
            rows
        };
        
        let duration = start_time.elapsed();
        info!("Retrieved {} accounts in {:?}", result.len(), duration);
        
        Ok(result)
    }

    #[instrument(skip(self), fields(embedding_dim = %embedding.len(), limit = ?limit))]
    async fn search_similar_transactions(
        &self,
        embedding: Vec<f32>,
        limit: Option<u32>,
    ) -> Result<Vec<Value>> {
        let start_time = Instant::now();
        info!("Searching for similar transactions");
        
        let result = self.call_rpc(
            "search_similar_transactions",
            json!({
                "query_embedding": embedding,
                "match_count": resolve_limit(limit),
            }),
        ).await?;
        
        let duration = start_time.elapsed();
        info!("Found {} similar transactions in {:?}", result.len(), duration);
        
        Ok(result)
    }

    #[instrument(skip(self), fields(embedding_dim = %embedding.len(), limit = ?limit))]
    async fn search_similar_categories(
        &self,
        embedding: Vec<f32>,
        limit: Option<u32>,
    ) -> Result<Vec<Value>> {
        let start_time = Instant::now();
        info!("Searching for similar categories");
        
        let result = self.call_rpc(
            "search_similar_categories",
            json!({
                "query_embedding": embedding,
                "match_count": resolve_limit(limit),
            }),
        ).await?;
        
        let duration = start_time.elapsed();
        info!("Found {} similar categories in {:?}", result.len(), duration);
        
        Ok(result)
    }
}

impl SupabaseGateway {
    #[instrument(skip(self), fields(table = %table))]
    async fn insert_and_fetch(&self, table: &str, payload: Value) -> Result<Value> {
        let start_time = Instant::now();
        debug!("Inserting record into {}", table);
        
        let id = self
            .client
            .insert(table, payload)
            .await
            .map_err(|err| {
                error!("Failed to insert into {}: {}", table, err);
                anyhow!("failed to insert into {table}: {err}")
            })?;
        
        let result = self.fetch_by_id(table, &Self::normalize_id(&id)).await?;
        let duration = start_time.elapsed();
        debug!("Record inserted and fetched in {:?}", duration);
        
        Ok(result)
    }

    #[instrument(skip(self), fields(table = %table, filters = ?filters))]
    async fn fetch_first(&self, table: &str, filters: &[(&str, &str)]) -> Result<Option<Value>> {
        debug!("Fetching first record from {} with filters: {:?}", table, filters);
        
        let mut query = self.client.select(table).limit(1);
        for (column, value) in filters {
            query = query.eq(column, value);
        }

        let rows = query
            .execute()
            .await
            .map_err(|err| {
                error!("Failed to query {}: {}", table, err);
                anyhow!("failed to query {table}: {err}")
            })?;
        
        let result = rows.into_iter().next();
        debug!("Found {} records", if result.is_some() { 1 } else { 0 });
        
        Ok(result)
    }

    #[instrument(skip(self), fields(name = %name, account_type = %account_type))]
    async fn fetch_account(&self, name: &str, account_type: AccountType) -> Result<Option<Value>> {
        self.fetch_first(
            "accounts",
            &[("name", name), ("type", account_type.as_ref())],
        )
        .await
    }

    #[instrument(skip(self), fields(table = %table, id = %id))]
    async fn fetch_by_id(&self, table: &str, id: &str) -> Result<Value> {
        debug!("Fetching {} by id: {}", table, id);
        
        self.fetch_first(table, &[("id", id)])
            .await?
            .ok_or_else(|| {
                error!("{} record {} was not found", table, id);
                anyhow!("{table} record {id} was not found")
            })
    }

    fn extract_id(&self, value: &Value) -> Result<String> {
        value
            .get("id")
            .and_then(Value::as_str)
            .map(|id| id.to_string())
            .ok_or_else(|| {
                error!("Row missing id column");
                anyhow!("row missing id column")
            })
    }

    fn normalize_id(id: &str) -> String {
        id.trim_matches('"').to_string()
    }

    #[instrument(skip(self), fields(function = %function))]
    async fn call_rpc(&self, function: &str, payload: Value) -> Result<Vec<Value>> {
        let start_time = Instant::now();
        debug!("Calling RPC function: {}", function);
        
        let url = format!("{}/{}", self.rpc_base, function);
        let response = self
            .http
            .post(url)
            .headers(self.rpc_headers()?)
            .json(&payload)
            .send()
            .await
            .with_context(|| format!("RPC {function} request failed"))?;

        let result = if response.status().is_success() {
            response
                .json::<Vec<Value>>()
                .await
                .context("failed to parse RPC response")?
        } else {
            let status = response.status();
            let body = response.text().await.unwrap_or_default();
            error!("RPC {} failed ({}): {}", function, status, body);
            return Err(anyhow!("RPC {function} failed ({status}): {body}"));
        };
        
        let duration = start_time.elapsed();
        debug!("RPC {} completed in {:?} with {} results", function, duration, result.len());
        
        Ok(result)
    }

    #[instrument(skip(self))]
    fn rpc_headers(&self) -> Result<HeaderMap> {
        let mut headers = HeaderMap::new();
        headers.insert(
            "apikey",
            HeaderValue::from_str(&self.service_key).context("invalid apikey header value")?,
        );
        headers.insert(
            AUTHORIZATION,
            HeaderValue::from_str(&format!("Bearer {}", self.service_key))
                .context("invalid authorization header value")?,
        );
        headers.insert(CONTENT_TYPE, HeaderValue::from_static("application/json"));
        headers.insert(ACCEPT, HeaderValue::from_static("application/json"));
        headers.insert(
            "Accept-Profile",
            HeaderValue::from_str(&self.schema).context("invalid profile header")?,
        );
        headers.insert(
            "Content-Profile",
            HeaderValue::from_str(&self.schema).context("invalid profile header")?,
        );
        Ok(headers)
    }
}

fn resolve_limit(limit: Option<u32>) -> u32 {
    limit.unwrap_or(5).clamp(1, 25)
}
