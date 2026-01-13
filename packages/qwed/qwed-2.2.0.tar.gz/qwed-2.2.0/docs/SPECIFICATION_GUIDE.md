# QWED Verification: Specification Guide

> **TL;DR:** QWED verifies LLM outputs against **developer-written code specifications**, not natural language. If you let the LLM generate both the answer AND the spec, you've just verified a hallucination.

## How QWED Actually Works

```
┌─────────────────────────────────────────────────────────────┐
│                    CORRECT USAGE                            │
├─────────────────────────────────────────────────────────────┤
│  Developer provides:  expected_value = "100000 * 1.05**10"  │
│  LLM generates:       answer = "150000"                     │
│  QWED verifies:       150000 ≠ 162889.46 → REJECTED         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    INCORRECT USAGE                          │
├─────────────────────────────────────────────────────────────┤
│  LLM generates:       expected_value = "100000 * 1.05**5"   │
│  LLM generates:       answer = "127628"                     │
│  QWED verifies:       127628 ≈ 127628.16 → VERIFIED ❌      │
│  (Hallucination verified because spec was also hallucinated)│
└─────────────────────────────────────────────────────────────┘
```

## The Golden Rule

| Component | Who Provides It | Example |
|-----------|-----------------|---------|
| **Specification** | Developer (you) | `expected = "P * (1 + r)**n"` |
| **LLM Output** | LLM | `"$150,000"` |
| **Ground Truth** | Developer (you) | `P=100000, r=0.05, n=10` |

**QWED does NOT solve:** Natural language → Formal specification translation.

**QWED DOES solve:** "Is this LLM output correct given my known ground truth?"

---

## Examples by Engine

### Math Engine
```python
from qwed_new.core.verifier import VerificationEngine

engine = VerificationEngine()

# ✅ CORRECT: Developer provides formula
result = engine.verify_compound_interest(
    principal=100000,      # Developer knows this
    rate=0.05,             # Developer knows this  
    time=10,               # Developer knows this
    n=1,                   # Developer knows this
    expected=150000        # LLM claimed this
)
# Result: is_correct=False, calculated=162889.46

# ❌ WRONG: Letting LLM provide the formula
# If LLM says "use rate=0.03" and you trust it, QWED can't help
```

### SQL Engine
```python
from qwed_new.core.sql_verifier import SQLVerifier

verifier = SQLVerifier()

# ✅ CORRECT: Developer defines allowed tables
result = verifier.verify_query(
    query="SELECT * FROM users",           # LLM generated
    allowed_tables=["users", "orders"],    # Developer defines
    allowed_columns=["id", "name", "email"] # Developer defines
)

# ❌ WRONG: Letting LLM define what tables are allowed
```

### Code Engine
```python
from qwed_new.core.code_verifier import CodeSecurityVerifier

verifier = CodeSecurityVerifier()

# ✅ CORRECT: Developer defines forbidden patterns
result = verifier.analyze_code(
    code="eval(user_input)",  # LLM generated
    # Verifier has built-in dangerous pattern detection
)
# Result: UNSAFE - eval detected

# The patterns (eval, exec, __import__) are defined by QWED, not LLM
```

### Logic Engine
```python
from qwed_new.core.logic_verifier import LogicVerifier

verifier = LogicVerifier()

# ✅ CORRECT: Developer provides premises
result = verifier.verify_conclusion(
    premises=["All humans are mortal", "Socrates is human"],  # Developer
    conclusion="Socrates is mortal"  # LLM claimed
)

# ❌ WRONG: Letting LLM provide premises
# If LLM says "All humans are immortal", QWED will verify wrong logic
```

---

## When QWED Does NOT Work

| Use Case | Why It Fails |
|----------|--------------|
| "Verify this essay is factually correct" | No ground truth to compare against |
| "Check if this code does what I want" | "What you want" is ambiguous |
| "Validate this creative writing" | No deterministic correctness |
| "Verify this translation is accurate" | Requires semantic understanding |

---

## When QWED Works Best

| Use Case | Why It Works |
|----------|--------------|
| Financial calculations | Formula is known, answer must match |
| SQL query validation | Schema is known, query must follow rules |
| Code security scanning | Dangerous patterns are predefined |
| Logic proofs | Premises are given, conclusion must follow |
| Statistical claims | Data is known, statistics must be correct |

---

## Summary

| Question | Answer |
|----------|--------|
| Does QWED use LLMs to verify LLMs? | **No.** Uses SymPy, Z3, AST, SQLGlot. |
| Can QWED verify any LLM output? | **No.** Only structured, domain-specific outputs. |
| Who provides the ground truth? | **You, the developer.** |
| What if the spec is wrong? | **Output will be wrong.** Same as any software. |

---

*"Math verifies the proof, not the premise. If you hallucinate the constraints, you've verified a hallucination."*

— Valid criticism we agree with. That's why specs come from you, not the LLM.
