# QWEDLocal - Client-Side Verification

**Run QWED verification directly in your code without a backend server!**

## 🌟 Why QWEDLocal?

### **No Backend Server Needed**
- Run verification directly in your application
- No infrastructure to manage
- Perfect for prototyping, scripts, and small projects

### **100% Privacy**
- Your API keys stay on your machine
- Your data never touches QWED servers
- Perfect for HIPAA, GDPR, sensitive data

### **Model Agnostic**
- Works with **ANY LLM** - OpenAI, Anthropic, Gemini
- Works with **local models** via Ollama (FREE!)
- Works with **any OpenAI-compatible API**

### **Smart Caching**
- Automatic result caching saves API costs
- 50-80% cost reduction on repeated queries
- 10x faster for cache hits

---

## 📦 Installation

```bash
pip install qwed
```

**Dependencies:**
```bash
# For different LLM providers
pip install openai         # OpenAI + Ollama
pip install anthropic      # Anthropic Claude
pip install google-generativeai  # Google Gemini

# For verification engines
pip install sympy          # Math verification
pip install z3-solver      # Logic verification

# For caching and CLI
pip install colorama click
```

---

## 🚀 Quick Start

### Option 1: Ollama (FREE! $0/month)

```bash
# 1. Install Ollama
# Visit: https://ollama.com

# 2. Pull a model
ollama pull llama3

# 3. Start Ollama
ollama serve
```

```python
from qwed_sdk import QWEDLocal

client = QWEDLocal(
    base_url="http://localhost:11434/v1",
    model="llama3"
)

result = client.verify_math("What is 2+2?")
print(result.verified)  # True
print(result.value)  # 4
```

### Option 2: OpenAI

```python
from qwed_sdk import QWEDLocal

client = QWEDLocal(
    provider="openai",
    api_key="sk-proj-...",
    model="gpt-4o-mini"  # Budget-friendly!
)

result = client.verify_math("What is the derivative of x^2?")
print(result.verified)  # True
print(result.value)  # 2*x
```

### Option 3: Anthropic Claude

```python
from qwed_sdk import QWEDLocal

client = QWEDLocal(
    provider="anthropic",
    api_key="sk-ant-...",
    model="claude-3-haiku-20240307"
)

result = client.verify("What is 5 factorial?")
```

---

## 🔬 Verification Engines

### 1. Math Verification (SymPy)

```python
result = client.verify_math("What is the integral of 2x?")
print(result.value)  # x**2
print(result.evidence)  # {"method": "sympy_eval", ...}
```

### 2. Logic Verification (Z3)

```python
result = client.verify_logic("Is (p AND NOT p) satisfiable?")
print(result.value)  # FALSE (contradiction!)
print(result.evidence)  # {"method": "z3_sat", ...}
```

### 3. Code Security (AST)

```python
code = """
def safe_function():
    return 42
"""

result = client.verify_code(code)
print(result.value)  # "SAFE"
```

**Dangerous code detection:**

```python
dangerous_code = """
import os
eval(user_input)
"""

result = client.verify_code(dangerous_code)
print(result.value)  # "UNSAFE"
print(result.evidence["dangerous_patterns"])
# ["Dangerous function: eval"]
```

---

## ⚡ Smart Caching

**Automatic caching saves API costs!**

```python
# First call - hits LLM ($$$)
result = client.verify_math("2+2")
# -> 🔬 QWED Verification | Math Engine
# -> 📝 LLM Response: 4
# -> ✅ VERIFIED → 4

# Second call - from cache (FREE!)
result = client.verify_math("2+2")
# -> ⚡ Cache HIT (saved API call!)
# -> Returns instantly!
```

**Cache stats:**

```python
stats = client.cache_stats
print(f"Hit rate: {stats.hit_rate:.1%}")
print(f"Hits: {stats.hits}, Misses: {stats.misses}")
```

**Disable caching:**

```python
client = QWEDLocal(
    provider="openai",
    api_key="...",
    cache=False  # Always fresh
)
```

---

## 🎨 CLI Tool

### One-Shot Verification

```bash
# Basic usage
qwed verify "What is 2+2?"

# With specific provider
qwed verify "derivative of x^2" --provider openai --model gpt-4o-mini

# With Ollama
qwed verify "5!" --base-url http://localhost:11434/v1 --model llama3

# Quiet mode (for scripts)
qwed verify "2+2" --quiet
```

### Interactive Mode

```bash
qwed interactive

# Output:
🔬 QWED Interactive Mode
Type 'exit' or 'quit' to quit

> What is 2+2?
🔬 QWED Verification | Math Engine
📝 LLM Response: 4
✅ VERIFIED → 4

> exit
```

### Cache Management

```bash
# View cache stats
qwed cache stats

# Clear cache
qwed cache clear
```

### Help

```bash
qwed --help
qwed verify --help
qwed interactive --help
```

---

## 🎯 Cost Comparison

| Tier | Monthly Cost | LLM Options | Best For |
|------|-------------|-------------|----------|
| **Local** | **$0** | Ollama (Llama 3, Mistral, Phi) | Students, Privacy, Development |
| **Budget** | **~$5-10** | GPT-4o-mini, Gemini Flash | Startups, Prototypes |
| **Premium** | **~$50-100** | GPT-4, Claude Opus | Enterprises, Production |

**With caching: 50-80% cost reduction!**

---

## 🔒 Privacy \u0026 Security

### **Your Data Never Leaves Your Machine**

**QWEDLocal architecture:**

```
┌─────────────────────────────────────┐
│ Your Machine                        │
│                                     │
│  ┌──────────────┐                  │
│  │ QWEDLocal    │                  │
│  │ (Your Code)  │                  │
│  └──────┬───────┘                  │
│         │                           │
│         ├─→ LLM API (Direct)       │
│         │   (OpenAI/Anthropic/     │
│         │    Ollama)                │
│         │                           │
│         └─→ Verifiers (Local)      │
│             SymPy, Z3, AST          │
│                                     │
│  ❌ NO data sent to QWED!          │
└─────────────────────────────────────┘
```

**Perfect for:**
- Healthcare (HIPAA compliance)
- Finance (PCI-DSS compliance)
- Government (classified data)
- Privacy-focused applications

---

## 🔧 Advanced Configuration

### Custom Cache Settings

```python
client = QWEDLocal(
    provider="openai",
    api_key="...",
    cache=True,
    cache_ttl=3600  # 1 hour TTL (default: 24 hours)
)
```

### Environment Variables

```bash
export QWED_API_KEY="sk-..."
export QWED_QUIET=1  # Disable colorful output
```

### Quiet Mode (No Branding)

```python
import os
os.environ["QWED_QUIET"] = "1"

client = QWEDLocal(...)
result = client.verify("2+2")
# No colored output, just results
```

---

## 📊 Examples

### Example 1: Fact Checking Pipeline

```python
from qwed_sdk import QWEDLocal

client = QWEDLocal(base_url="http://localhost:11434/v1", model="llama3")

facts_to_check = [
    "2+2=4",
    "The derivative of x^2 is 2x",
    "Paris is the capital of France"
]

for fact in facts_to_check:
    result = client.verify(fact)
    print(f"{fact}: {'✅' if result.verified else '❌'}")
```

### Example 2: Code Review Automation

```python
import os
from qwed_sdk import QWEDLocal

client = QWEDLocal(provider="openai", api_key=os.getenv("OPENAI_API_KEY"))

code_snippets = [
    "def add(a, b): return a + b",
    "exec(user_input)",  # Dangerous!
    "import os; os.system('rm -rf /')"  # Very dangerous!
]

for code in code_snippets:
    result = client.verify_code(code)
    status = "🟢 SAFE" if result.verified else "🔴 UNSAFE"
    print(f"{status}: {code[:30]}...")
    if not result.verified:
        print(f"  Issues: {result.evidence['dangerous_patterns']}")
```

### Example 3: Batch Processing with Cache

```python
from qwed_sdk import QWEDLocal

client = QWEDLocal(provider="openai", api_key="...")

# Process 1000 math queries
queries = ["What is 2+2?"] * 500 + ["What is 3+3?"] * 500

for q in queries:
    result = client.verify_math(q)
    # First 2 calls hit LLM, rest cached!

print(client.cache_stats)
# Hit rate: 99.8%! (Saved $$$)
```

---

## 🐛 Troubleshooting

### LLM Not Available

```python
# Check if Ollama is running
curl http://localhost:11434/v1/models

# Start Ollama
ollama serve
```

### Missing Dependencies

```bash
# Install verification engines
pip install sympy z3-solver

# Install LLM clients
pip install openai anthropic google-generativeai
```

### Cache Issues

```bash
# Clear cache
qwed cache clear

# Or in Python
client._cache.clear()
```

---

## 🎓 Learn More

- **[CLI Guide](CLI.md)** - Complete CLI reference
- **[Ollama Integration](OLLAMA_INTEGRATION.md)** - FREE local LLMs
- **[LLM Configuration](LLM_CONFIGURATION.md)** - All provider setups
- **[Full Documentation](https://docs.qwedai.com)** - Complete docs

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## 📝 License

Apache 2.0 - See [LICENSE](../LICENSE)

---

## ⭐ Support

If QWEDLocal saved you time or money, give us a star! ⭐

**Made with 💜 by the QWED team**
