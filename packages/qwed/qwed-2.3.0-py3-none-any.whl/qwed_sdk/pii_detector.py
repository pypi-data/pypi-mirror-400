"""
PII Detection and Masking for QWED.

Enterprise privacy feature that detects and masks personally identifiable 
information (PII) before sending data to LLM providers.

Requires optional dependencies:
    pip install qwed[pii]
    python -m spacy download en_core_web_lg
"""

from typing import Dict, List, Optional, Tuple

# Lazy imports to avoid forcing dependency
PIIDetectorType = None


def check_pii_dependencies():
    """Check if PII dependencies are installed."""
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine, OperatorConfig
        return True
    except ImportError:
        return False


def raise_missing_dependencies():
    """Raise helpful error if PII dependencies missing."""
    raise ImportError(
        "\n"
        "⚠️  PII masking features require additional packages.\n"
        "\n"
        "📦 Install with:\n"
        "   pip install 'qwed[pii]'\n"
        "\n"
        "📥 Then download the spaCy model:\n"
        "   python -m spacy download en_core_web_lg\n"
        "\n"
        "📖 See docs/PII_MASKING.md for details.\n"
    )


class PIIDetector:
    """
    Detect and mask PII using Microsoft Presidio.
    
    Supports detection of:
    - EMAIL_ADDRESS
    - CREDIT_CARD
    - PHONE_NUMBER
    - US_SSN
    - IBAN_CODE
    - IP_ADDRESS
    - PERSON (names)
    - LOCATION
    - MEDICAL_LICENSE
    
    Example:
        >>> detector = PIIDetector()
        >>> masked, info = detector.detect_and_mask("Email: john@example.com")
        >>> print(masked)
        "Email: <EMAIL_ADDRESS>"
        >>> print(info["pii_detected"])
        1
    """
    
    # Supported PII entity types
    ENTITIES = [
        "EMAIL_ADDRESS",
        "CREDIT_CARD",
        "PHONE_NUMBER",
        "US_SSN",
        "IBAN_CODE",
        "IP_ADDRESS",
        "PERSON",
        "LOCATION",
        "MEDICAL_LICENSE"
    ]
    
    def __init__(self, entities: Optional[List[str]] = None):
        """
        Initialize PII detector.
        
        Args:
            entities: Optional list of entity types to detect.
                     If None, uses all supported entities.
        
        Raises:
            ImportError: If presidio dependencies not installed.
        """
        if not check_pii_dependencies():
            raise_missing_dependencies()
        
        # Import here (lazy) to avoid forcing dependency
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        
        self.entities = entities or self.ENTITIES
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
    
    def detect_and_mask(self, text: str) -> Tuple[str, Dict]:
        """
        Detect PII and return masked text + metadata.
        
        Args:
            text: Input text to scan for PII
        
        Returns:
            Tuple of (masked_text, metadata_dict)
            
        Metadata includes:
            - pii_detected: Count of PII entities found
            - types: List of entity types detected
            - positions: List of (start, end) positions
            - original_length: Length of original text
            - masked_length: Length of masked text
            
        Example:
            >>> detector.detect_and_mask("Call me at 555-1234")
            ("Call me at <PHONE_NUMBER>", {
                "pii_detected": 1,
                "types": ["PHONE_NUMBER"],
                ...
            })
        """
        # Analyze for PII
        results = self.analyzer.analyze(
            text=text,
            entities=self.entities,
            language='en'
        )
        
        # No PII found
        if not results:
            return text, {"pii_detected": 0}
        
        # Import operator config for masking
        from presidio_anonymizer import OperatorConfig
        
        # Anonymize with entity type placeholders
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators={
                "DEFAULT": OperatorConfig(
                    "replace",
                    {"new_value": lambda x: f"<{x.entity_type}>"}
                )
            }
        )
        
        # Build metadata
        metadata = {
            "pii_detected": len(results),
            "types": [r.entity_type for r in results],
            "positions": [(r.start, r.end) for r in results],
            "original_length": len(text),
            "masked_length": len(anonymized.text)
        }
        
        return anonymized.text, metadata
