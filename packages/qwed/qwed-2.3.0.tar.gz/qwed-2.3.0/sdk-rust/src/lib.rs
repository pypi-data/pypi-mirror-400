//! QWED Rust SDK
//!
//! A Rust client for the QWED Verification Protocol.
//!
//! # Example
//! ```rust,no_run
//! use qwed::QWEDClient;
//!
//! #[tokio::main]
//! async fn main() -> Result<(), qwed::Error> {
//!     let client = QWEDClient::new("qwed_your_api_key");
//!     let result = client.verify("What is 2+2?").await?;
//!     println!("Verified: {}", result.verified);
//!     Ok(())
//! }
//! ```

use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::Duration;

// ============================================================================
// Types
// ============================================================================

/// Verification type/engine
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "snake_case")]
pub enum VerificationType {
    #[default]
    NaturalLanguage,
    Math,
    Logic,
    Stats,
    Fact,
    Code,
    Sql,
    Image,
    Reasoning,
}

/// Verification result status
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "UPPERCASE")]
pub enum VerificationStatus {
    Verified,
    Failed,
    Corrected,
    Blocked,
    Error,
    Timeout,
    Unsupported,
}

/// Verification request
#[derive(Debug, Clone, Serialize)]
pub struct VerificationRequest {
    pub query: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub r#type: Option<VerificationType>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub params: Option<HashMap<String, serde_json::Value>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub options: Option<RequestOptions>,
}

/// Request options
#[derive(Debug, Clone, Serialize, Default)]
pub struct RequestOptions {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timeout_ms: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub include_proof: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub include_attestation: Option<bool>,
}

/// Verification response
#[derive(Debug, Clone, Deserialize)]
pub struct VerificationResponse {
    pub status: VerificationStatus,
    pub verified: bool,
    #[serde(default)]
    pub engine: Option<String>,
    #[serde(default)]
    pub result: Option<HashMap<String, serde_json::Value>>,
    #[serde(default)]
    pub attestation: Option<String>,
    #[serde(default)]
    pub error: Option<ErrorInfo>,
    #[serde(default)]
    pub metadata: Option<ResponseMetadata>,
}

/// Error information
#[derive(Debug, Clone, Deserialize)]
pub struct ErrorInfo {
    pub code: String,
    pub message: String,
    #[serde(default)]
    pub details: Option<HashMap<String, serde_json::Value>>,
}

/// Response metadata
#[derive(Debug, Clone, Deserialize)]
pub struct ResponseMetadata {
    pub request_id: Option<String>,
    pub latency_ms: Option<f64>,
    pub protocol_version: Option<String>,
}

/// Batch item
#[derive(Debug, Clone, Serialize)]
pub struct BatchItem {
    pub query: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub r#type: Option<VerificationType>,
}

/// Batch response
#[derive(Debug, Clone, Deserialize)]
pub struct BatchResponse {
    pub job_id: String,
    pub status: String,
    #[serde(default)]
    pub summary: Option<BatchSummary>,
    #[serde(default)]
    pub items: Vec<BatchResult>,
}

/// Batch summary
#[derive(Debug, Clone, Deserialize)]
pub struct BatchSummary {
    pub total: u32,
    pub verified: u32,
    pub failed: u32,
    pub success_rate: f64,
}

/// Batch result item
#[derive(Debug, Clone, Deserialize)]
pub struct BatchResult {
    pub id: String,
    pub status: VerificationStatus,
    pub verified: bool,
    #[serde(default)]
    pub result: Option<HashMap<String, serde_json::Value>>,
    #[serde(default)]
    pub error: Option<ErrorInfo>,
}

// ============================================================================
// Errors
// ============================================================================

/// QWED Error type
#[derive(Debug, thiserror::Error)]
pub enum Error {
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),
    
    #[error("API error [{code}]: {message}")]
    Api { code: String, message: String },
    
    #[error("Authentication failed")]
    Auth,
    
    #[error("Rate limit exceeded")]
    RateLimit,
    
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
}

// ============================================================================
// Client
// ============================================================================

/// QWED API Client
pub struct QWEDClient {
    api_key: String,
    base_url: String,
    client: Client,
}

impl QWEDClient {
    /// Create a new QWED client
    pub fn new(api_key: impl Into<String>) -> Self {
        Self::with_options(api_key, "http://localhost:8000", Duration::from_secs(30))
    }

    /// Create a client with custom options
    pub fn with_options(
        api_key: impl Into<String>,
        base_url: impl Into<String>,
        timeout: Duration,
    ) -> Self {
        Self {
            api_key: api_key.into(),
            base_url: base_url.into().trim_end_matches('/').to_string(),
            client: Client::builder()
                .timeout(timeout)
                .build()
                .expect("Failed to create HTTP client"),
        }
    }

    /// Check API health
    pub async fn health(&self) -> Result<HashMap<String, serde_json::Value>, Error> {
        self.get("/health").await
    }

    /// Verify a natural language query
    pub async fn verify(&self, query: &str) -> Result<VerificationResponse, Error> {
        let req = VerificationRequest {
            query: query.to_string(),
            r#type: Some(VerificationType::NaturalLanguage),
            params: None,
            options: None,
        };
        self.post("/verify/natural_language", &req).await
    }

    /// Verify a math expression
    pub async fn verify_math(&self, expression: &str) -> Result<VerificationResponse, Error> {
        let mut body = HashMap::new();
        body.insert("expression", expression);
        self.post("/verify/math", &body).await
    }

    /// Verify a QWED-Logic expression
    pub async fn verify_logic(&self, query: &str) -> Result<VerificationResponse, Error> {
        let mut body = HashMap::new();
        body.insert("query", query);
        self.post("/verify/logic", &body).await
    }

    /// Verify code for security vulnerabilities
    pub async fn verify_code(&self, code: &str, language: &str) -> Result<VerificationResponse, Error> {
        let mut body = HashMap::new();
        body.insert("code", code);
        body.insert("language", language);
        self.post("/verify/code", &body).await
    }

    /// Verify a factual claim
    pub async fn verify_fact(&self, claim: &str, context: &str) -> Result<VerificationResponse, Error> {
        let mut body = HashMap::new();
        body.insert("claim", claim);
        body.insert("context", context);
        self.post("/verify/fact", &body).await
    }

    /// Verify a SQL query
    pub async fn verify_sql(&self, query: &str, schema: &str, dialect: &str) -> Result<VerificationResponse, Error> {
        let mut body = HashMap::new();
        body.insert("query", query);
        body.insert("schema_ddl", schema);
        body.insert("dialect", dialect);
        self.post("/verify/sql", &body).await
    }

    /// Batch verification
    pub async fn verify_batch(&self, items: Vec<BatchItem>) -> Result<BatchResponse, Error> {
        let mut body = HashMap::new();
        body.insert("items", items);
        self.post("/verify/batch", &body).await
    }

    // HTTP helpers
    async fn get<T: for<'de> Deserialize<'de>>(&self, path: &str) -> Result<T, Error> {
        let response = self.client
            .get(format!("{}{}", self.base_url, path))
            .header("X-API-Key", &self.api_key)
            .send()
            .await?;

        self.handle_response(response).await
    }

    async fn post<T: for<'de> Deserialize<'de>, B: Serialize>(&self, path: &str, body: &B) -> Result<T, Error> {
        let response = self.client
            .post(format!("{}{}", self.base_url, path))
            .header("X-API-Key", &self.api_key)
            .header("Content-Type", "application/json")
            .json(body)
            .send()
            .await?;

        self.handle_response(response).await
    }

    async fn handle_response<T: for<'de> Deserialize<'de>>(&self, response: reqwest::Response) -> Result<T, Error> {
        let status = response.status();
        
        if status == 401 {
            return Err(Error::Auth);
        }
        
        if status == 429 {
            return Err(Error::RateLimit);
        }
        
        if !status.is_success() {
            let text = response.text().await.unwrap_or_default();
            return Err(Error::Api {
                code: format!("HTTP-{}", status.as_u16()),
                message: text,
            });
        }

        Ok(response.json().await?)
    }
}

// ============================================================================
// Helpers
// ============================================================================

/// Check if a response indicates successful verification
pub fn is_verified(response: &VerificationResponse) -> bool {
    response.verified
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_verification_type_serialization() {
        let t = VerificationType::Math;
        let json = serde_json::to_string(&t).unwrap();
        assert_eq!(json, "\"math\"");
    }

    #[test]
    fn test_verification_status_deserialization() {
        let json = "\"VERIFIED\"";
        let status: VerificationStatus = serde_json::from_str(json).unwrap();
        assert_eq!(status, VerificationStatus::Verified);
    }
}
