# QWED Integration Guide

Complete guide for integrating QWED verification into popular AI frameworks.

---

## Quick Start: 5-Minute Integration

```python
# Install
pip install qwed

# Use in any LLM workflow
from qwed_new.core.verifier import VerificationEngine

engine = VerificationEngine()
result = engine.verify_math("2 + 2", expected_value=4)
print(result["is_correct"])  # True
```

---

## Framework Integrations

### 1. LangChain Integration

#### Basic Usage

```python
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from qwed_sdk.langchain import QWEDTool

# Create QWED verification tools
math_tool = QWEDTool(verification_type="math")
code_tool = QWEDTool(verification_type="code")
sql_tool = QWEDTool(verification_type="sql")

# Create LangChain agent with QWED
llm = ChatOpenAI(model="gpt-4")
tools = [math_tool, code_tool, sql_tool]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Always verify your calculations and code."),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Use it
response = agent_executor.invoke({
    "input": "Calculate compound interest: $100,000 at 5% for 10 years"
})
```

#### Advanced: Auto-Verification Chain

```python
from langchain.chains import LLMChain
from qwed_sdk.langchain import QWEDVerificationChain

# Wrap any LangChain chain with automatic verification
base_chain = LLMChain(llm=llm, prompt=prompt)

# QWED automatically verifies all math/code outputs
verified_chain = QWEDVerificationChain(
    llm_chain=base_chain,
    verification_engines=["math", "code", "sql"],
    reject_unverified=True  # Halt on failed verification
)

result = verified_chain.run("What is 15% of $250?")
# Automatically verified before returning
```

---

### 2. CrewAI Integration

#### Agent-Level Verification

```python
from crewai import Agent, Task, Crew
from qwed_sdk.crewai import QWEDVerifiedAgent

# Create agent with built-in verification
analyst = QWEDVerifiedAgent(
    role="Financial Analyst",
    goal="Perform accurate financial calculations",
    backstory="Expert in finance with zero tolerance for calculation errors",
    verification_engines=["math"],  # Auto-verify all math outputs
    allow_unverified=False  # Reject unverified outputs
)

# Create task
task = Task(
    description="Calculate NPV of cash flows: [-1000, 300, 300, 300, 300] at 10% discount rate",
    agent=analyst
)

# QWED automatically verifies before task completion
crew = Crew(agents=[analyst], tasks=[task])
result = crew.kickoff()
```

#### Multi-Agent with Different Verification Needs

```python
from qwed_sdk.crewai import QWEDVerifiedAgent

# Math-focused agent
quant = QWEDVerifiedAgent(
    role="Quantitative Analyst",
    verification_engines=["math", "stats"],
    allow_unverified=False
)

# Code-focused agent
engineer = QWEDVerifiedAgent(
    role="Software Engineer", 
    verification_engines=["code", "sql"],
    allow_unverified=False
)

# General agent (allows unverified creative output)
writer = Agent(
    role="Content Writer",
    # No verification needed for creative writing
)

crew = Crew(agents=[quant, engineer, writer], tasks=[...])
```

---

### 3. LlamaIndex Integration

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from qwed_sdk.llamaindex import QWEDQueryEngine

# Create index
documents = SimpleDirectoryReader("./data").load_data()
index = VectorStoreIndex.from_documents(documents)

# Wrap query engine with QWED verification
base_engine = index.as_query_engine()
verified_engine = QWEDQueryEngine(
    base_engine=base_engine,
    verification_engines=["math", "fact"],  # Verify calculations and facts
)

# Query with automatic verification
response = verified_engine.query(
    "Based on the financial reports, what was the YoY growth rate?"
)
# Math automatically verified against source documents
```

---

### 4. Standalone API Integration

#### REST API

```python
import requests

response = requests.post(
    "https://api.qwedai.com/v1/verify",
    headers={"X-API-Key": "qwed_..."},
    json={
        "domain": "math",
        "query": "What is the derivative of x^2?",
        "llm_output": "2x",
        "options": {
            "strict_mode": True,
            "timeout_ms": 5000
        }
    }
)

result = response.json()
print(result["verified"])  # True
print(result["attestation"])  # JWT proof
```

#### Python SDK

```python
from qwed_sdk import QWEDClient

client = QWEDClient(api_key="qwed_...")

# Verify any LLM output
result = client.verify(
    domain="code",
    code=llm_generated_code,
    check_security=True
)

if result.is_safe:
    execute(llm_generated_code)
else:
    print(f"Blocked: {result.issues}")
```

---

## Common Patterns

### Pattern 1: Pre-Execution Verification

```python
def safe_execute_llm_code(llm_code: str):
    """Execute LLM-generated code only after verification."""
    from qwed_new.core.code_verifier import CodeVerifier
    
    verifier = CodeVerifier()
    result = verifier.verify_code(llm_code)
    
    if not result["is_safe"]:
        raise SecurityError(f"Code rejected: {result['issues']}")
    
    # Safe to execute
    exec(llm_code)
```

### Pattern 2: Fallback on Verification Failure

```python
def verified_llm_call(prompt: str, max_retries=3):
    """Call LLM and verify, retry on failure."""
    from qwed_new.core.verifier import VerificationEngine
    
    engine = VerificationEngine()
    
    for attempt in range(max_retries):
        llm_output = call_llm(prompt)
        result = engine.verify_math(llm_output["answer"])
        
        if result["is_correct"]:
            return llm_output
        
        # Retry with feedback
        prompt += f"\\nPrevious answer {llm_output['answer']} was incorrect. Correct answer is {result['calculated_value']}."
    
    raise ValueError("LLM failed verification after retries")
```

### Pattern 3: Batch Verification

```python
from qwed_new.core.code_verifier import CodeVerifier

verifier = CodeVerifier()

# Verify multiple snippets at once
snippets = [
    {"code": snippet1, "language": "python"},
    {"code": snippet2, "language": "javascript"},
]

results = verifier.verify_batch(snippets)
print(f"Safe: {results['summary']['safe_count']}")
print(f"Blocked: {results['summary']['blocked_count']}")
```

---

## Production Deployment

### Docker Compose

```yaml
version: '3.8'

services:
  qwed-api:
    image: qwedai/qwed-verification:latest
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Environment Variables

```bash
# .env
QWED_API_KEY=qwed_sk_...
QWED_TIMEOUT_MS=5000
QWED_STRICT_MODE=true
QWED_ENABLE_ATTESTATION=true
```

---

## Performance Tips

1. **Cache Results:** Use Redis for repeated verifications
2. **Async Verification:** Don't block LLM calls
3. **Selective Domains:** Only enable engines you need
4. **Timeout Tuning:** Adjust based on complexity

```python
# Optimized configuration
from qwed_sdk import QWEDClient

client = QWEDClient(
    api_key="qwed_...",
    timeout_ms=3000,  # 3 second timeout
    cache_enabled=True,
    engines=["math", "code"]  # Only what you need
)
```

---

## Troubleshooting

### Issue: Verification Timeouts

**Solution:** Reduce complexity or increase timeout

```python
verifier = VerificationEngine()
result = verifier.verify_code(
    code,
    timeout_seconds=60  # Increase from default 30s
)
```

### Issue: False Rejections

**Solution:** Use tolerance for floating-point math

```python
result = engine.verify_math(
    "0.1 + 0.2",
    expected_value=0.3,
    tolerance=0.001  # Allow small rounding errors
)
```

### Issue: Unsupported Domain

**Solution:** Check domain coverage

```python
result = verifier.verify_code(code)

if result["status"] == "UNSUPPORTED":
    # Fall back to static analysis only
    use_alternative_verification()
```

---

## Examples Repository

Full working examples: https://github.com/QWED-AI/qwed-verification/tree/main/examples

- ✅ LangChain agent with financial calculations
- ✅ CrewAI multi-agent with code verification
- ✅ LlamaIndex RAG with fact checking
- ✅ FastAPI integration
- ✅ Streamlit UI with live verification

---

**Need help?** Open an issue: https://github.com/QWED-AI/qwed-verification/issues
