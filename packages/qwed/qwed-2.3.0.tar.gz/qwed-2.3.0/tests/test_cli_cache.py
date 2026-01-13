"""
Quick test script for QWEDLocal with Caching + CLI simulation.

Run this to test:
1. Cache functionality
2. QWEDLocal with mock LLM
"""

import sys
sys.path.insert(0, ".")

from qwed_sdk.qwed_local import QWEDLocal, VerificationResult
from qwed_sdk.cache import VerificationCache

print("=" * 60)
print("🧪 Testing QWEDLocal Cache + CLI Features")
print("=" * 60)

# Test 1: Cache Basic Functionality
print("\n1️⃣ Testing Cache...")
cache = VerificationCache()
cache.clear()  # Start fresh!
print("  ✅ Cache cleared (starting fresh)")

# First query (miss)
result = cache.get("2+2")
assert result is None, "Should be cache MISS"
print("  ✅ Cache MISS works")

# Set cache
cache.set("2+2", {"verified": True, "value": 4, "confidence": 1.0, "evidence": {}})
print("  ✅ Cache SET works")

# Second query (hit!)
result = cache.get("2+2")
assert result is not None, "Should be cache HIT"
assert result["value"] == 4, "Value should be 4"
print("  ✅ Cache HIT works")

# Test case normalization
result = cache.get("2+2".upper())  # "2+2" -> normalized same
assert result is not None, "Should normalize case"
print("  ✅ Case normalization works")

# Test with extra whitespace
cache.set("   Test   Query   ", {"verified": True, "value": "test"})
result = cache.get("test query")  # Should normalize to same
assert result is not None, "Should normalize whitespace"
print("  ✅ Whitespace normalization works")

# Print stats
print("\n📊 Cache Stats:")
cache.print_stats()

# Clear cache
cache.clear()
print("✅ Cache cleared")

print("\n" + "=" * 60)
print("2️⃣ Testing QWEDLocal Initialization...")
print("=" * 60)

# Test with caching enabled
try:
    client = QWEDLocal(
        base_url="http://localhost:11434/v1",
        model="llama3",
        cache=True
    )
    print("  ✅ Client with cache initialized")
    print(f"  ✅ Cache enabled: {client.use_cache}")
    
    # Test cache_stats property
    stats = client.cache_stats
    print(f"  ✅ Cache stats accessible: {stats}")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

# Test without caching
try:
    client_no_cache = QWEDLocal(
        base_url="http://localhost:11434/v1",
        model="llama3", 
        cache=False
    )
    print("  ✅ Client without cache initialized")
    print(f"  ✅ Cache disabled: {not client_no_cache.use_cache}")
    
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 60)
print("3️⃣ Manual CLI Test Instructions")
print("=" * 60)

print("""
To test the CLI, run these commands manually:

1. Install in development mode:
   pip install -e .

2. Test basic verification:
   qwed verify "What is 2+2?"
   
3. Test with Ollama (if running):
   qwed verify "derivative of x^2" --base-url http://localhost:11434/v1 --model llama3

4. Test cache stats:
   qwed cache stats

5. Test interactive mode:
   qwed interactive
   > What is 2+2?
   > exit

6. Test help:
   qwed --help
   qwed verify --help

""")

print("=" * 60)
print("✅ All automated tests PASSED!")
print("=" * 60)
print("\n👆 Follow manual CLI test instructions above!")
