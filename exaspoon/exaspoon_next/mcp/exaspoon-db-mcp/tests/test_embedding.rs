//! Tests for embedding service.

use exaspoon_db_mcp::embedding::Embedder;

mod common;

#[tokio::test]
async fn test_mock_embedder_embed() {
    let embedder = common::MockEmbedder::new(vec![0.1, 0.2, 0.3]);
    
    let result = embedder.embed("test text").await.unwrap();
    assert_eq!(result, vec![0.1, 0.2, 0.3]);
    
    let calls = embedder.calls();
    assert_eq!(calls.len(), 1);
    assert_eq!(calls[0], "test text");
}

#[tokio::test]
async fn test_mock_embedder_maybe_embed_with_text() {
    let embedder = common::MockEmbedder::new(vec![0.4, 0.5, 0.6]);
    
    let result = embedder.maybe_embed(Some("test text")).await.unwrap();
    assert_eq!(result, Some(vec![0.4, 0.5, 0.6]));
    
    let calls = embedder.calls();
    assert_eq!(calls.len(), 1);
    assert_eq!(calls[0], "test text");
}

#[tokio::test]
async fn test_mock_embedder_maybe_embed_without_text() {
    let embedder = common::MockEmbedder::new(vec![0.7, 0.8, 0.9]);
    
    let result = embedder.maybe_embed(None).await.unwrap();
    assert_eq!(result, None);
    
    let calls = embedder.calls();
    assert_eq!(calls.len(), 0);
}

#[tokio::test]
async fn test_mock_embedder_clear_calls() {
    let embedder = common::MockEmbedder::new(vec![0.1, 0.2, 0.3]);
    
    // Make some calls
    embedder.embed("test1").await.unwrap();
    embedder.embed("test2").await.unwrap();
    
    assert_eq!(embedder.calls().len(), 2);
    
    // Clear calls
    embedder.clear_calls();
    assert_eq!(embedder.calls().len(), 0);
}

#[tokio::test]
async fn test_mock_embedder_multiple_calls() {
    let embedder = common::MockEmbedder::new(vec![0.1, 0.2, 0.3]);
    
    embedder.embed("test1").await.unwrap();
    embedder.embed("test2").await.unwrap();
    embedder.embed("test3").await.unwrap();
    
    let calls = embedder.calls();
    assert_eq!(calls.len(), 3);
    assert_eq!(calls[0], "test1");
    assert_eq!(calls[1], "test2");
    assert_eq!(calls[2], "test3");
}

// Note: We can't test the actual EmbeddingService without mocking the OpenAI client,
// which would require more complex setup. The MockEmbedder provides sufficient testing
// for the Embedder trait interface used by the server.
