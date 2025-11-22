mod config;
mod embedding;
mod models;
mod server;
mod supabase;

use crate::{
    config::AppConfig,
    embedding::{Embedder, EmbeddingService},
    server::ExaspoonDbServer,
    supabase::{Database, SupabaseGateway},
};
use anyhow::Result;
use rmcp::{transport::stdio, ServiceExt};
use std::sync::Arc;
use std::time::Instant;
use tracing::info;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

#[tokio::main]
async fn main() -> Result<()> {
    let start_time = Instant::now();
    
    // Load environment variables
    dotenvy::dotenv().ok();
    
    // Initialize basic logging first
    let env_filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("exaspoon_db_mcp=info"));
    
    tracing_subscriber::registry()
        .with(env_filter)
        .with(
            tracing_subscriber::fmt::layer()
                .with_writer(std::io::stderr)
                .with_ansi(false)
        )
        .init();
    
    // Load and validate configuration
    info!("Loading configuration");
    let config = AppConfig::from_env()?;
    info!("Configuration loaded successfully");
    info!("Supabase URL: {}", &config.supabase_url[..config.supabase_url.find('.').unwrap_or(config.supabase_url.len())]);
    info!("Embedding model: {}", config.embedding_model);
    info!("Log level: {}", config.log_level);
    
    info!("Starting Exaspoon DB MCP Server");
    
    // Initialize services
    info!("Initializing Supabase gateway");
    let supabase: Arc<dyn Database> = Arc::new(SupabaseGateway::new(&config)?);
    info!("Supabase gateway initialized");
    
    info!("Initializing embedding service");
    let embedder: Arc<dyn Embedder> = Arc::new(EmbeddingService::new(
        &config.openai_api_key,
        config.openai_base_url.as_deref(),
        &config.embedding_model,
    )?);
    info!("Embedding service initialized");
    
    // Start the MCP server
    info!("Starting MCP server");
    let service = ExaspoonDbServer::new(supabase, embedder)
        .serve(stdio())
        .await?;
    
    let startup_time = start_time.elapsed();
    info!("Server started successfully in {:?}", startup_time);
    
    info!("Waiting for MCP connections");
    service.waiting().await?;
    
    Ok(())
}
