// Package qwed provides a Go client for the QWED Verification Protocol.
//
// Example usage:
//
//	client := qwed.NewClient("qwed_your_api_key")
//	result, err := client.Verify("What is 2+2?")
//	if err != nil {
//	    log.Fatal(err)
//	}
//	fmt.Println(result.Verified) // true
package qwed

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// ============================================================================
// Types
// ============================================================================

// VerificationType represents the type of verification to perform.
type VerificationType string

const (
	TypeNaturalLanguage VerificationType = "natural_language"
	TypeMath            VerificationType = "math"
	TypeLogic           VerificationType = "logic"
	TypeStats           VerificationType = "stats"
	TypeFact            VerificationType = "fact"
	TypeCode            VerificationType = "code"
	TypeSQL             VerificationType = "sql"
	TypeImage           VerificationType = "image"
	TypeReasoning       VerificationType = "reasoning"
)

// VerificationStatus represents the result status.
type VerificationStatus string

const (
	StatusVerified    VerificationStatus = "VERIFIED"
	StatusFailed      VerificationStatus = "FAILED"
	StatusCorrected   VerificationStatus = "CORRECTED"
	StatusBlocked     VerificationStatus = "BLOCKED"
	StatusError       VerificationStatus = "ERROR"
	StatusTimeout     VerificationStatus = "TIMEOUT"
	StatusUnsupported VerificationStatus = "UNSUPPORTED"
)

// VerificationRequest represents a verification request.
type VerificationRequest struct {
	Query   string                 `json:"query"`
	Type    VerificationType       `json:"type,omitempty"`
	Params  map[string]interface{} `json:"params,omitempty"`
	Options *RequestOptions        `json:"options,omitempty"`
}

// RequestOptions configures request behavior.
type RequestOptions struct {
	TimeoutMs            int  `json:"timeout_ms,omitempty"`
	IncludeProof         bool `json:"include_proof,omitempty"`
	IncludeAttestation   bool `json:"include_attestation,omitempty"`
}

// VerificationResponse represents the API response.
type VerificationResponse struct {
	Status      VerificationStatus     `json:"status"`
	Verified    bool                   `json:"verified"`
	Engine      string                 `json:"engine,omitempty"`
	Result      map[string]interface{} `json:"result,omitempty"`
	Attestation string                 `json:"attestation,omitempty"`
	Error       *ErrorInfo             `json:"error,omitempty"`
	Metadata    *ResponseMetadata      `json:"metadata,omitempty"`
}

// ErrorInfo contains error details.
type ErrorInfo struct {
	Code    string                 `json:"code"`
	Message string                 `json:"message"`
	Details map[string]interface{} `json:"details,omitempty"`
}

// ResponseMetadata contains response metadata.
type ResponseMetadata struct {
	RequestID       string  `json:"request_id,omitempty"`
	LatencyMs       float64 `json:"latency_ms,omitempty"`
	ProtocolVersion string  `json:"protocol_version,omitempty"`
}

// BatchRequest represents a batch verification request.
type BatchRequest struct {
	Items   []BatchItem    `json:"items"`
	Options *BatchOptions  `json:"options,omitempty"`
}

// BatchItem represents a single item in a batch.
type BatchItem struct {
	Query string           `json:"query"`
	Type  VerificationType `json:"type,omitempty"`
}

// BatchOptions configures batch behavior.
type BatchOptions struct {
	MaxParallel int  `json:"max_parallel,omitempty"`
	FailFast    bool `json:"fail_fast,omitempty"`
}

// BatchResponse represents the batch API response.
type BatchResponse struct {
	JobID   string        `json:"job_id"`
	Status  string        `json:"status"`
	Summary *BatchSummary `json:"summary,omitempty"`
	Items   []BatchResult `json:"items,omitempty"`
}

// BatchSummary contains batch statistics.
type BatchSummary struct {
	Total       int     `json:"total"`
	Verified    int     `json:"verified"`
	Failed      int     `json:"failed"`
	SuccessRate float64 `json:"success_rate"`
}

// BatchResult represents a single batch item result.
type BatchResult struct {
	ID       string                 `json:"id"`
	Status   VerificationStatus     `json:"status"`
	Verified bool                   `json:"verified"`
	Result   map[string]interface{} `json:"result,omitempty"`
	Error    *ErrorInfo             `json:"error,omitempty"`
}

// ============================================================================
// Errors
// ============================================================================

// QWEDError represents a QWED API error.
type QWEDError struct {
	Code       string
	Message    string
	StatusCode int
}

func (e *QWEDError) Error() string {
	return fmt.Sprintf("QWED Error [%s]: %s", e.Code, e.Message)
}

// ============================================================================
// Client
// ============================================================================

// Client is the QWED API client.
type Client struct {
	apiKey     string
	baseURL    string
	httpClient *http.Client
}

// ClientOption configures the client.
type ClientOption func(*Client)

// WithBaseURL sets a custom base URL.
func WithBaseURL(url string) ClientOption {
	return func(c *Client) {
		c.baseURL = url
	}
}

// WithTimeout sets the HTTP timeout.
func WithTimeout(timeout time.Duration) ClientOption {
	return func(c *Client) {
		c.httpClient.Timeout = timeout
	}
}

// WithHTTPClient sets a custom HTTP client.
func WithHTTPClient(client *http.Client) ClientOption {
	return func(c *Client) {
		c.httpClient = client
	}
}

// NewClient creates a new QWED client.
func NewClient(apiKey string, opts ...ClientOption) *Client {
	c := &Client{
		apiKey:  apiKey,
		baseURL: "http://localhost:8000",
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}

	for _, opt := range opts {
		opt(c)
	}

	return c
}

// ============================================================================
// API Methods
// ============================================================================

// Health checks the API health status.
func (c *Client) Health(ctx context.Context) (map[string]interface{}, error) {
	var result map[string]interface{}
	err := c.request(ctx, "GET", "/health", nil, &result)
	return result, err
}

// Verify performs a natural language verification.
func (c *Client) Verify(ctx context.Context, query string) (*VerificationResponse, error) {
	return c.VerifyWithOptions(ctx, query, nil)
}

// VerifyWithOptions performs verification with custom options.
func (c *Client) VerifyWithOptions(ctx context.Context, query string, opts *RequestOptions) (*VerificationResponse, error) {
	req := &VerificationRequest{
		Query:   query,
		Type:    TypeNaturalLanguage,
		Options: opts,
	}

	var resp VerificationResponse
	err := c.request(ctx, "POST", "/verify/natural_language", req, &resp)
	return &resp, err
}

// VerifyMath verifies a mathematical expression.
func (c *Client) VerifyMath(ctx context.Context, expression string) (*VerificationResponse, error) {
	req := map[string]interface{}{
		"expression": expression,
	}

	var resp VerificationResponse
	err := c.request(ctx, "POST", "/verify/math", req, &resp)
	return &resp, err
}

// VerifyLogic verifies a QWED-Logic DSL expression.
func (c *Client) VerifyLogic(ctx context.Context, query string) (*VerificationResponse, error) {
	req := map[string]interface{}{
		"query": query,
	}

	var resp VerificationResponse
	err := c.request(ctx, "POST", "/verify/logic", req, &resp)
	return &resp, err
}

// VerifyCode checks code for security vulnerabilities.
func (c *Client) VerifyCode(ctx context.Context, code, language string) (*VerificationResponse, error) {
	req := map[string]interface{}{
		"code":     code,
		"language": language,
	}

	var resp VerificationResponse
	err := c.request(ctx, "POST", "/verify/code", req, &resp)
	return &resp, err
}

// VerifyFact verifies a factual claim against context.
func (c *Client) VerifyFact(ctx context.Context, claim, factContext string) (*VerificationResponse, error) {
	req := map[string]interface{}{
		"claim":   claim,
		"context": factContext,
	}

	var resp VerificationResponse
	err := c.request(ctx, "POST", "/verify/fact", req, &resp)
	return &resp, err
}

// VerifySQL validates a SQL query against a schema.
func (c *Client) VerifySQL(ctx context.Context, query, schemaDDL, dialect string) (*VerificationResponse, error) {
	req := map[string]interface{}{
		"query":      query,
		"schema_ddl": schemaDDL,
		"dialect":    dialect,
	}

	var resp VerificationResponse
	err := c.request(ctx, "POST", "/verify/sql", req, &resp)
	return &resp, err
}

// VerifyBatch processes multiple verifications concurrently.
func (c *Client) VerifyBatch(ctx context.Context, items []BatchItem, opts *BatchOptions) (*BatchResponse, error) {
	req := map[string]interface{}{
		"items":   items,
		"options": opts,
	}

	var resp BatchResponse
	err := c.request(ctx, "POST", "/verify/batch", req, &resp)
	return &resp, err
}

// ============================================================================
// HTTP Helpers
// ============================================================================

func (c *Client) request(ctx context.Context, method, path string, body, result interface{}) error {
	var bodyReader io.Reader
	if body != nil {
		data, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("failed to marshal request: %w", err)
		}
		bodyReader = bytes.NewReader(data)
	}

	req, err := http.NewRequestWithContext(ctx, method, c.baseURL+path, bodyReader)
	if err != nil {
		return fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-API-Key", c.apiKey)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode >= 400 {
		var errResp struct {
			Error *ErrorInfo `json:"error"`
		}
		json.Unmarshal(data, &errResp)

		code := fmt.Sprintf("HTTP-%d", resp.StatusCode)
		message := string(data)
		if errResp.Error != nil {
			code = errResp.Error.Code
			message = errResp.Error.Message
		}

		return &QWEDError{
			Code:       code,
			Message:    message,
			StatusCode: resp.StatusCode,
		}
	}

	if result != nil {
		if err := json.Unmarshal(data, result); err != nil {
			return fmt.Errorf("failed to unmarshal response: %w", err)
		}
	}

	return nil
}

// ============================================================================
// Helpers
// ============================================================================

// IsVerified returns true if the response indicates successful verification.
func IsVerified(resp *VerificationResponse) bool {
	return resp != nil && resp.Verified
}
