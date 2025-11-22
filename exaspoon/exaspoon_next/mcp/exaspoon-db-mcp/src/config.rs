use anyhow::{Context, Result};
use tracing::Level;

#[derive(Debug, Clone)]
pub struct AppConfig {
    pub supabase_url: String,
    pub supabase_service_key: String,
    pub openai_api_key: String,
    pub openai_base_url: Option<String>,
    pub embedding_model: String,
    pub log_level: Level,
}

impl AppConfig {
    pub fn from_env() -> Result<Self> {
        let log_level = std::env::var("LOG_LEVEL")
            .unwrap_or_else(|_| "info".to_string())
            .parse::<Level>()
            .unwrap_or(Level::INFO);
        
        Ok(Self {
            supabase_url: Self::require("SUPABASE_URL")?,
            supabase_service_key: Self::require("SUPABASE_SERVICE_KEY")?,
            openai_api_key: Self::require("OPENAI_API_KEY")?,
            openai_base_url: std::env::var("OPENAI_BASE_URL")
                .ok()
                .filter(|value| !value.is_empty()),
            embedding_model: std::env::var("EMBEDDING_MODEL")
                .ok()
                .filter(|value| !value.is_empty())
                .unwrap_or_else(|| "text-embedding-3-large".to_string()),
            log_level,
        })
    }

    fn require(key: &str) -> Result<String> {
        std::env::var(key).with_context(|| format!("Missing required env var {key}"))
    }
}
