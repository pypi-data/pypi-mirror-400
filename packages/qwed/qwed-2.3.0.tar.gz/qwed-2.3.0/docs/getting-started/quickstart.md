# Quick Start

Run your first QWED verification in 60 seconds.

## Verify a Math Calculation

```bash
curl -X POST http://localhost:8000/verify/math \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 15% of 200?"}'
```

### Response

```json
{
  "status": "VERIFIED",
  "final_answer": 30.0,
  "verification": {
    "is_correct": true,
    "calculated_value": 30.0,
    "expression": "0.15 * 200"
  },
  "latency_ms": 245.3
}
```

---

## Verify Business Logic

Test if an invoice passes your business rules:

```bash
curl -X POST http://localhost:8000/verify/logic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Invoice total is $1000, subtotal is $900, tax is $100. Is this valid?"
  }'
```

---

## Verify SQL Safety

Check if AI-generated SQL is safe:

```bash
curl -X POST http://localhost:8000/verify/sql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "SELECT * FROM users WHERE id = 1; DROP TABLE users;--"
  }'
```

### Response

```json
{
  "is_safe": false,
  "blocked_reason": "Destructive command detected: DROP TABLE",
  "severity": "CRITICAL"
}
```

---

## Using the Python SDK

```python
from qwed import QwedClient

client = QwedClient(api_key="your_api_key")

# Verify a calculation
result = client.verify_math("What is the compound interest on $1000 at 5% for 3 years?")

print(f"Answer: {result.final_answer}")
print(f"Status: {result.status}")
```

---

## Next Steps

- Explore the [API Reference](../api.md) for all endpoints
- Learn about [Security Features](../security.md)
- Deep dive into the [Architecture](../architecture.md)

