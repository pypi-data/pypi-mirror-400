---
title: 'QWED: A Deterministic Verification Protocol for Large Language Model Outputs'
tags:
  - Python
  - LLM
  - verification
  - formal-methods
  - AI-safety
authors:
  - name: Rahul Dass
    orcid: 0009-0000-2088-7487
    affiliation: 1
affiliations:
  - name: QWED-AI
    index: 1
date: 28 December 2025
bibliography: paper.bib
---

# Summary

QWED (Query with Evidence & Determinism) is a Python framework that provides deterministic verification for Large Language Model (LLM) outputs. Unlike approaches that attempt to reduce hallucinations through fine-tuning or prompting, QWED treats LLMs as untrusted translators and verifies their outputs using formal methods.

The framework includes eight specialized verification engines:
- **Math Engine**: Uses SymPy for symbolic computation verification
- **Logic Engine**: Uses Z3 SMT solver for propositional and first-order logic
- **Code Engine**: Uses AST analysis for security pattern detection
- **SQL Engine**: Uses SQLGlot for query validation
- **Statistics Engine**: Verifies statistical claims deterministically
- **Fact Engine**: Checks factual grounding with TF-IDF and NLI
- **Image Engine**: Validates image metadata claims
- **Consensus Engine**: Cross-references multiple LLM providers

# Statement of Need

LLMs exhibit fundamental unreliability in deterministic tasks. In benchmarks against Claude Opus 4.5, we observed accuracy rates of 73% for financial calculations, 81% for mathematical reasoning, and 85% for adversarial prompts. In regulated industries (finance, healthcare, legal), such error rates are unacceptable.

Existing approaches attempt to "reduce" hallucinations through:
- Fine-tuning (expensive, not generalizable)
- Retrieval-augmented generation (helps with knowledge, not reasoning)
- Multiple prompting (still probabilistic)

QWED takes a different approach: **verify, don't correct**. If an output cannot be proven correct, it is rejected before reaching production.

# Features

- **Deterministic**: All verification uses provable methods (SymPy, Z3, AST)
- **Production-ready**: Designed for enterprise integration
- **Framework-agnostic**: Works with LangChain, CrewAI, or any LLM
- **Observable**: Built-in telemetry and audit logging
- **Extensible**: Plugin architecture for custom engines

# Example Usage

```python
from qwed_new.core.verifier import VerificationEngine

engine = VerificationEngine()

# LLM claims derivative of x^2 is 3x (incorrect)
result = engine.verify_derivative("x**2", "x", "3*x")
# Returns: is_correct=False, calculated_derivative="2*x"
```

# Acknowledgements

QWED builds on the work of the SymPy, Z3, and SQLGlot communities.

# References
