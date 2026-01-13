# qwed-go

> Go SDK for QWED Verification Protocol

[![Go Reference](https://pkg.go.dev/badge/github.com/qwed-ai/qwed-go.svg)](https://pkg.go.dev/github.com/qwed-ai/qwed-go)
[![Go 1.21+](https://img.shields.io/badge/go-1.21%2B-blue.svg)](https://golang.org/)

## Installation

```bash
go get github.com/qwed-ai/qwed-go
```

## Quick Start

```go
package main

import (
    "context"
    "fmt"
    "log"

    "github.com/qwed-ai/qwed-go"
)

func main() {
    client := qwed.NewClient("qwed_your_api_key")
    
    result, err := client.Verify(context.Background(), "What is 2+2?")
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Println(result.Verified) // true
    fmt.Println(result.Status)   // VERIFIED
}
```

## Verification Methods

### Natural Language

```go
result, err := client.Verify(ctx, "Is 15% of 200 equal to 30?")
```

### Math Expressions

```go
result, err := client.VerifyMath(ctx, "x**2 + 2*x + 1 = (x+1)**2")
```

### Logic (QWED-DSL)

```go
result, err := client.VerifyLogic(ctx, "(AND (GT x 5) (LT y 10))")
// result.Result["satisfiability"] = "SAT"
// result.Result["model"] = map[string]interface{}{"x": 6, "y": 9}
```

### Code Security

```go
result, err := client.VerifyCode(ctx, `
import os
os.system('rm -rf /')
`, "python")
```

### Fact Verification

```go
result, err := client.VerifyFact(ctx,
    "Paris is the capital of France",
    "France is a country in Europe. Its capital city is Paris.",
)
```

### SQL Validation

```go
result, err := client.VerifySQL(ctx,
    "SELECT * FROM users WHERE id = 1",
    "CREATE TABLE users (id INT PRIMARY KEY, name TEXT)",
    "postgresql",
)
```

## Batch Verification

```go
items := []qwed.BatchItem{
    {Query: "2+2=4", Type: qwed.TypeMath},
    {Query: "3*3=9", Type: qwed.TypeMath},
    {Query: "(AND (GT x 5))", Type: qwed.TypeLogic},
}

result, err := client.VerifyBatch(ctx, items, nil)
fmt.Printf("Success rate: %.1f%%\n", result.Summary.SuccessRate)
```

## Client Options

```go
client := qwed.NewClient(
    "qwed_...",
    qwed.WithBaseURL("https://api.qwed.ai"),
    qwed.WithTimeout(60 * time.Second),
)
```

## Error Handling

```go
result, err := client.Verify(ctx, "test")
if err != nil {
    if qwedErr, ok := err.(*qwed.QWEDError); ok {
        switch qwedErr.StatusCode {
        case 401:
            log.Println("Invalid API key")
        case 429:
            log.Println("Rate limited")
        default:
            log.Printf("Error %s: %s", qwedErr.Code, qwedErr.Message)
        }
    }
}
```

## Context Support

All methods accept a context for cancellation and timeouts:

```go
ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
defer cancel()

result, err := client.Verify(ctx, "What is 2+2?")
```

## Types

| Type | Description |
|------|-------------|
| `VerificationType` | Enum: Math, Logic, Stats, Fact, Code, SQL, etc. |
| `VerificationStatus` | Enum: VERIFIED, FAILED, CORRECTED, BLOCKED, etc. |
| `VerificationResponse` | Full verification result |
| `BatchResponse` | Batch operation result |

## License

Apache 2.0

