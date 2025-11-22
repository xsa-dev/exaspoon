//! Tests for configuration loading and validation.

use exaspoon_db_mcp::config::AppConfig;
use std::env;

mod common;

#[test]
fn test_config_from_env_with_all_variables() {
    // Set all required environment variables
    env::set_var("SUPABASE_URL", "https://test.supabase.co");
    env::set_var("SUPABASE_SERVICE_KEY", "test-service-key");
    env::set_var("OPENAI_API_KEY", "test-openai-key");
    env::set_var("OPENAI_BASE_URL", "https://test.openai.com");
    env::set_var("EMBEDDING_MODEL", "text-embedding-3-large");

    let config = AppConfig::from_env().unwrap();

    assert_eq!(config.supabase_url, "https://test.supabase.co");
    assert_eq!(config.supabase_service_key, "test-service-key");
    assert_eq!(config.openai_api_key, "test-openai-key");
    assert_eq!(config.openai_base_url, Some("https://test.openai.com".to_string()));
    assert_eq!(config.embedding_model, "text-embedding-3-large");

    // Clean up
    env::remove_var("SUPABASE_URL");
    env::remove_var("SUPABASE_SERVICE_KEY");
    env::remove_var("OPENAI_API_KEY");
    env::remove_var("OPENAI_BASE_URL");
    env::remove_var("EMBEDDING_MODEL");
}

#[test]
fn test_config_from_env_with_minimal_variables() {
    // Set only required environment variables
    env::set_var("SUPABASE_URL", "https://test.supabase.co");
    env::set_var("SUPABASE_SERVICE_KEY", "test-service-key");
    env::set_var("OPENAI_API_KEY", "test-openai-key");

    let config = AppConfig::from_env().unwrap();

    assert_eq!(config.supabase_url, "https://test.supabase.co");
    assert_eq!(config.supabase_service_key, "test-service-key");
    assert_eq!(config.openai_api_key, "test-openai-key");
    assert_eq!(config.openai_base_url, None);
    assert_eq!(config.embedding_model, "text-embedding-3-large"); // Default value

    // Clean up
    env::remove_var("SUPABASE_URL");
    env::remove_var("SUPABASE_SERVICE_KEY");
    env::remove_var("OPENAI_API_KEY");
}

#[test]
fn test_config_from_env_with_empty_optional_variables() {
    // Set required variables and empty optional ones
    env::set_var("SUPABASE_URL", "https://test.supabase.co");
    env::set_var("SUPABASE_SERVICE_KEY", "test-service-key");
    env::set_var("OPENAI_API_KEY", "test-openai-key");
    env::set_var("OPENAI_BASE_URL", ""); // Empty string
    env::set_var("EMBEDDING_MODEL", ""); // Empty string

    let config = AppConfig::from_env().unwrap();

    assert_eq!(config.supabase_url, "https://test.supabase.co");
    assert_eq!(config.supabase_service_key, "test-service-key");
    assert_eq!(config.openai_api_key, "test-openai-key");
    assert_eq!(config.openai_base_url, None); // Empty string should be treated as None
    assert_eq!(config.embedding_model, "text-embedding-3-large"); // Default value for empty string

    // Clean up
    env::remove_var("SUPABASE_URL");
    env::remove_var("SUPABASE_SERVICE_KEY");
    env::remove_var("OPENAI_API_KEY");
    env::remove_var("OPENAI_BASE_URL");
    env::remove_var("EMBEDDING_MODEL");
}

#[test]
fn test_config_from_env_missing_supabase_url() {
    // Clear all environment variables first
    env::remove_var("SUPABASE_URL");
    env::remove_var("SUPABASE_SERVICE_KEY");
    env::remove_var("OPENAI_API_KEY");
    
    env::set_var("SUPABASE_SERVICE_KEY", "test-service-key");
    env::set_var("OPENAI_API_KEY", "test-openai-key");
    // Don't set SUPABASE_URL

    let result = AppConfig::from_env();
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("Missing required env var SUPABASE_URL"));

    // Clean up
    env::remove_var("SUPABASE_SERVICE_KEY");
    env::remove_var("OPENAI_API_KEY");
}

#[test]
fn test_config_from_env_missing_supabase_service_key() {
    // Clear all environment variables first
    env::remove_var("SUPABASE_URL");
    env::remove_var("SUPABASE_SERVICE_KEY");
    env::remove_var("OPENAI_API_KEY");
    
    env::set_var("SUPABASE_URL", "https://test.supabase.co");
    env::set_var("OPENAI_API_KEY", "test-openai-key");
    // Don't set SUPABASE_SERVICE_KEY

    let result = AppConfig::from_env();
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("Missing required env var SUPABASE_SERVICE_KEY"));

    // Clean up
    env::remove_var("SUPABASE_URL");
    env::remove_var("OPENAI_API_KEY");
}

#[test]
fn test_config_from_env_missing_openai_api_key() {
    // Clear all environment variables first
    env::remove_var("SUPABASE_URL");
    env::remove_var("SUPABASE_SERVICE_KEY");
    env::remove_var("OPENAI_API_KEY");
    
    env::set_var("SUPABASE_URL", "https://test.supabase.co");
    env::set_var("SUPABASE_SERVICE_KEY", "test-service-key");
    // Don't set OPENAI_API_KEY

    let result = AppConfig::from_env();
    assert!(result.is_err());
    assert!(result.unwrap_err().to_string().contains("Missing required env var OPENAI_API_KEY"));

    // Clean up
    env::remove_var("SUPABASE_URL");
    env::remove_var("SUPABASE_SERVICE_KEY");
}
