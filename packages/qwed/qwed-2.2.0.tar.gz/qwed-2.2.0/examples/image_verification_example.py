"""
QWED Image Verification Example.

Demonstrates:
1. Using the core ImageVerifier directly (SDK support pending).
2. Verifying claims about image dimensions and content.
"""

from qwed_new.core.image_verifier import ImageVerifier
# Note: SDK support coming soon. Currently use core library directly.

def main():
    # Initialize verifier
    # For full functionality, a VLM provider would be passed here
    verifier = ImageVerifier(use_vlm_fallback=False)

    # Create a dummy image (1x1 red pixel PNG)
    # This is just for demonstration purposes
    import base64
    # 1x1 red pixel
    dummy_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    image_bytes = base64.b64decode(dummy_image_b64)

    print("--- Image Verification (Core Library) ---")

    # 1. Verify Dimensions
    claim_size = "The image is 1x1 pixels"
    print(f"Claim: {claim_size}")

    result = verifier.verify_image(image_bytes, claim_size)
    print(f"Verdict: {result['verdict']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reasoning: {result['reasoning']}")
    print()

    # 2. Verify Color (Simple check)
    claim_color = "The image contains red"
    print(f"Claim: {claim_color}")

    # Without VLM, this might return VLM_REQUIRED or try basic analysis
    result = verifier.verify_image(image_bytes, claim_color)
    print(f"Verdict: {result['verdict']}")
    print(f"Reasoning: {result['reasoning']}")

if __name__ == "__main__":
    main()
