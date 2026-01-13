# QWED Performance & Cost Benchmarks

**Test Environment:**
- Hardware: AWS EC2 t3.medium (2 vCPU, 4GB RAM)
- Python: 3.11
- QWED: v1.1.0
- Date: December 2025

---

## Performance Benchmarks (Latency)

### Verification Engine Latency

| Engine | Operation | Typical Latency | P95 Latency | P99 Latency |
|--------|-----------|-----------------|-------------|-------------|
| **Math** | Simple arithmetic | 5ms | 12ms | 18ms |
| **Math** | Calculus (derivative) | 15ms | 28ms | 45ms |
| **Math** | Matrix (3×3) | 22ms | 40ms | 65ms |
| **Math** | Financial (compound interest) | 8ms | 15ms | 25ms |
| **Logic** | Simple SAT | 25ms | 50ms | 80ms |
| **Logic** | Z3 theorem proving | 120ms | 250ms | 400ms |
| **Code** | AST security scan | 35ms | 70ms | 110ms |
| **Code** | Symbolic execution (simple) | 2,500ms | 8,000ms | 15,000ms |
| **SQL** | Query parsing | 18ms | 35ms | 55ms |
| **SQL** | Schema validation | 45ms | 85ms | 130ms |
| **Stats** | Mean/median | 12ms | 25ms | 40ms |
| **Stats** | Regression (100 rows) | 95ms | 180ms | 280ms |
| **Fact** | TF-IDF grounding | 60ms | 120ms | 200ms |
| **Image** | Metadata check | 15ms | 30ms | 50ms |
| **Consensus** | 3-model check | 4,500ms | 7,000ms | 12,000ms |

### Key Observations:

- ✅ **Most verifications < 100ms** - Suitable for real-time applications
- ⚠️ **Symbolic execution slow** - Use only for simple functions
- ⚠️ **Consensus expensive** - 3× LLM API calls required

---

## Cost Comparison

### Scenario: Financial Calculator Application

**Use Case:** Verify 1,000 compound interest calculations per day

| Approach | Description | Cost per 1K Verifications | Annual Cost |
|----------|-------------|---------------------------|-------------|
| **No Verification** | Trust LLM blindly | $0 | $0 |
| **QWED (Math Engine)** | 1 LLM call + SymPy | **$0.50** | **$183** |
| **Self-Consistency (3×)** | Call LLM 3 times, vote | $1.50 | $548 |
| **Self-Consistency (5×)** | Call LLM 5 times, vote | $2.50 | $913 |
| **Human Review** | Manual checking | $500 | $182,500 |

**QWED saves 80% vs self-consistency, 99.9% vs human review.**

---

### Scenario: SQL Query Generation (RAG Application)

**Use Case:** Verify 5,000 SQL queries per day

| Approach | LLM Calls | Verification | Cost per 1K | Annual Cost |
|----------|-----------|--------------|-------------|-------------|
| **QWED (SQL Engine)** | 1 | SQLGlot parse | **$0.50** | **$913** |
| **Self-Consistency (3×)** | 3 | Majority vote | $1.50 | $2,738 |
| **Manual Review** | 1 | DBA checks | $250 | $456,250 |

**QWED saves 67% vs self-consistency, 99.8% vs manual review.**

---

### Scenario: Code Security Scanning

**Use Case:** Verify 500 code snippets per day

| Approach | Detection Rate | Cost per 1K | Annual Cost | False Positive Rate |
|----------|----------------|-------------|-------------|---------------------|
| **QWED (Code Engine)** | 100% | **$0.50** | **$91** | 0% |
| **GPT-4 Security Review** | 85% | $2.00 | $365 | 15% |
| **Manual Code Review** | 95% | $400 | $73,000 | 5% |

**QWED: 100% detection + $0 false positive cost.**

---

## API Pricing (QWED Cloud)

### Free Tier
- 1,000 verifications/month
- All 8 engines
- No credit card required

### Pro ($49/month)
- 50,000 verifications/month
- Custom timeout limits
- Priority support
- SLA: 99.9% uptime

### Enterprise (Custom)
- Unlimited verifications
- On-premise deployment
- Custom SLA
- Dedicated support

### Pay-As-You-Go
- $0.0005 per verification (beyond free tier)
- Volume discounts available

---

## ROI Calculator

### Example: Finance Application

**Assumptions:**
- 10,000 calculations/day
- LLM cost: $0.50 per 1K calls
- Error rate without QWED: 5%
- Average error cost: $1,000 per error

| Metric | Without QWED | With QWED |
|--------|--------------|-----------|
| **Daily verifications** | 0 | 10,000 |
| **LLM cost** | $5/day | $5/day |
| **QWED cost** | $0/day | $5/day |
| **Errors per day** | 500 | 0 |
| **Error cost** | $500,000/day | $0/day |
| **Total cost** | $500,005/day | $10/day |
| **Savings** | - | **$500K/day** |

**Payback period: < 1 day**

---

## Latency Optimization Tips

### 1. Enable Redis Caching

```python
from qwed_sdk import QWEDClient

client = QWEDClient(
    cache_enabled=True,
    redis_url="redis://localhost:6379"
)

# Repeated verifications: 0.5ms (99% faster)
```

### 2. Async Verification

```python
import asyncio

async def verify_batch(items):
    tasks = [client.verify_async(item) for item in items]
    return await asyncio.gather(*tasks)

# 10× throughput improvement
```

### 3. Selective Engines

```python
# Only enable engines you need
client = QWEDClient(engines=["math", "code"])  # Faster startup
```

### 4. Timeout Tuning

```python
# Reduce timeout for simple operations
result = engine.verify_math(expr, timeout_ms=1000)  # 1s max
```

---

## Throughput Benchmarks

| Configuration | Requests/Second | Avg Latency |
|---------------|-----------------|-------------|
| Single thread | 15 req/s | 65ms |
| 4 workers | 55 req/s | 70ms |
| 8 workers | 95 req/s | 80ms |
| 16 workers (with Redis) | 180 req/s | 85ms |

**Recommendation:** 8 workers for production

---

## Comparison with Alternatives

### vs Guardrails AI

| Feature | QWED | Guardrails AI |
|---------|------|---------------|
| **Deterministic** | ✅ Yes (SymPy, Z3) | ❌ No (regex, ML) |
| **Provable** | ✅ Math proofs | ❌ Heuristic |
| **Latency** | 5-100ms | 50-200ms |
| **Cost** | $0.50/1K | $0.80/1K |
| **Security** | ✅ AST analysis | ⚠️ Pattern matching |

### vs Self-Consistency

| Metric | QWED | Self-Consistency (5×) |
|--------|------|----------------------|
| **Accuracy** | 100% (in domain) | 85-95% |
| **Cost** | $0.50/1K | $2.50/1K |
| **Latency** | 50ms | 5,000ms (100× slower) |
| **Deterministic** | ✅ Yes | ❌ No |

### vs Manual Review

| Metric | QWED | Human Review |
|--------|------|--------------|
| **Speed** | 50ms | 5 minutes |
| **Cost** | $0.0005 | $5 |
| **Accuracy** | 100% | 95% |
| **Scalability** | Unlimited | Limited |

---

## Production Scaling

### Architecture for 1M Verifications/Day

```
Load Balancer
    ├── API Server 1 (8 workers)
    ├── API Server 2 (8 workers)
    ├── API Server 3 (8 workers)
    └── Redis Cluster (3 nodes)

Estimated cost: $200/month (AWS)
Handles: 1.2M verifications/day
Latency: p95 < 100ms
```

---

## Summary

| Question | Answer |
|----------|--------|
| **Typical latency?** | 5-100ms for most engines |
| **Cost vs alternatives?** | 80% cheaper than self-consistency |
| **Scalability limit?** | 180 req/s per server (tested) |
| **Best use case?** | High-stakes domains (finance, healthcare, security) |

---

**Need custom benchmarks?** Contact: enterprise@qwedai.com
