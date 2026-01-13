"""
Simple unit test for QWEDLocal (no external dependencies).

Tests the basic structure without actually calling LLMs.
"""

import sys
sys.path.insert(0, ".")

from qwed_sdk.qwed_local import QWEDLocal, VerificationResult

def test_initialization():
    """Test QWEDLocal can be initialized."""
    print("Test 1: Initialization")
    
    # This should work (simulating Ollama)
    try:
        client = QWEDLocal(
            base_url="http://localhost:11434/v1",
            model="llama3"
        )
        print("  ✅ Ollama-style initialization SUCCESS")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False
    
    # Check client properties
    assert client.base_url == "http://localhost:11434/v1"
    assert client.model == "llama3"
    assert client.client_type == "openai"
    print("  ✅ Client properties correct")
    
    return True

def test_verification_result():
    """Test VerificationResult dataclass."""
    print("\nTest 2: VerificationResult")
    
    result = VerificationResult(
        verified=True,
        value=4,
        confidence=1.0,
        evidence={"method": "test"}
    )
    
    assert result.verified == True
    assert result.value == 4
    assert result.confidence == 1.0
    assert result.evidence["method"] == "test"
    print("  ✅ VerificationResult works")
    
    return True

def test_provider_validation():
    """Test that invalid providers are rejected."""
    print("\nTest 3: Provider Validation")
    
    try:
        # Should fail - no provider or base_url
        client = QWEDLocal(model="test")
        print("  ❌ Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"  ✅ Correctly rejected invalid config: {e}")
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("QWEDLocal Unit Tests")
    print("=" * 60)
    
    tests = [
        test_initialization,
        test_verification_result,
        test_provider_validation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ All tests PASSED!")
        sys.exit(0)
    else:
        print(f"\n❌ {failed} test(s) FAILED!")
        sys.exit(1)
