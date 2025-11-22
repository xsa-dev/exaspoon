use anyhow::{anyhow, Context, Result};
use async_openai::{config::OpenAIConfig, types::embeddings::CreateEmbeddingRequestArgs, Client};
use async_trait::async_trait;
use std::time::Instant;
use tracing::{debug, error, info, instrument, warn};

#[async_trait]
pub trait Embedder: Send + Sync {
    async fn embed(&self, text: &str) -> Result<Vec<f32>>;
    async fn maybe_embed(&self, text: Option<&str>) -> Result<Option<Vec<f32>>>;
}

#[derive(Clone)]
pub struct EmbeddingService {
    client: Client<OpenAIConfig>,
    model: String,
}

impl EmbeddingService {
    #[instrument(fields(model = %model, has_base_url = base_url.is_some()))]
    pub fn new(api_key: &str, base_url: Option<&str>, model: &str) -> Result<Self> {
        info!("Initializing embedding service");
        debug!("Using model: {}", model);
        
        let mut config = OpenAIConfig::new().with_api_key(api_key);
        if let Some(base) = base_url {
            debug!("Using custom base URL: {}", base);
            config = config.with_api_base(base);
        }
        
        let client = Client::with_config(config);
        
        info!("Embedding service initialized successfully");
        Ok(Self {
            client,
            model: model.to_string(),
        })
    }
}

#[async_trait]
impl Embedder for EmbeddingService {
    #[instrument(skip(self), fields(text_len = %text.len(), model = %self.model))]
    async fn embed(&self, text: &str) -> Result<Vec<f32>> {
        let start_time = Instant::now();
        debug!("Creating embedding for text (length: {})", text.len());
        
        let request = CreateEmbeddingRequestArgs::default()
            .model(self.model.clone())
            .input(text)
            .build()
            .context("failed to build embedding request")?;

        let response = self
            .client
            .embeddings()
            .create(request)
            .await
            .map_err(|err| {
                error!("Embedding request failed: {}", err);
                anyhow!("embedding request failed")
            })?;

        let result = response
            .data
            .into_iter()
            .next()
            .map(|item| item.embedding)
            .ok_or_else(|| {
                error!("OpenAI did not return embedding data");
                anyhow!("OpenAI did not return embedding data")
            })?;
        
        let duration = start_time.elapsed();
        info!("Embedding created successfully in {:?} (dimensions: {})", duration, result.len());
        
        Ok(result)
    }

    #[instrument(skip(self), fields(has_text = text.is_some()))]
    async fn maybe_embed(&self, text: Option<&str>) -> Result<Option<Vec<f32>>> {
        match text {
            Some(value) if !value.trim().is_empty() => {
                debug!("Text provided, creating embedding");
                Ok(Some(self.embed(value).await?))
            }
            Some(_value) => {
                warn!("Empty text provided, skipping embedding");
                Ok(None)
            }
            None => {
                debug!("No text provided, skipping embedding");
                Ok(None)
            }
        }
    }
}
