"""
QWED Benchmark Configuration

This file contains configuration for running benchmarks.
Users must set their own API keys as environment variables.

Environment Variables Required:
- AZURE_ENDPOINT: Your Azure/Anthropic API endpoint
- AZURE_API_KEY: Your API key

You can also use other LLM providers by modifying the call_llm() function.
"""

import os

# LLM API Configuration - SET YOUR OWN KEYS
AZURE_ENDPOINT = os.getenv(
    "AZURE_ENDPOINT", 
    "https://your-resource.services.ai.azure.com/anthropic/v1/messages"
)
AZURE_API_KEY = os.getenv("AZURE_API_KEY", "")

# Alternative: Use OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"

# Alternative: Use local Ollama
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434/api/generate")

# Model Configuration
DEFAULT_MODEL = os.getenv("BENCHMARK_MODEL", "claude-opus-4-5")

# Tolerance Settings
STRICT_TOLERANCE = 0.0001
FINANCE_TOLERANCE = 0.01

def validate_config():
    """Validate that API keys are configured"""
    if not AZURE_API_KEY and not OPENAI_API_KEY:
        print("=" * 60)
        print("⚠️  WARNING: No API keys configured!")
        print("=" * 60)
        print("Please set one of the following environment variables:")
        print("  - AZURE_API_KEY: For Azure/Anthropic Claude")
        print("  - OPENAI_API_KEY: For OpenAI GPT models")
        print("")
        print("Example:")
        print("  export AZURE_ENDPOINT='https://your-resource.services.ai.azure.com/anthropic/v1/messages'")
        print("  export AZURE_API_KEY='your-api-key-here'")
        print("=" * 60)
        return False
    return True

if __name__ == "__main__":
    if validate_config():
        print("✅ Configuration valid")
        print(f"   Endpoint: {AZURE_ENDPOINT}")
        print(f"   Model: {DEFAULT_MODEL}")
    else:
        print("❌ Configuration invalid - please set API keys")
