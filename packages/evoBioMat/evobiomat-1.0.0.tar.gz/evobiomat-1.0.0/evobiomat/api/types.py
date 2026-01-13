from dataclasses import dataclass
from typing import Optional

@dataclass
class VerificationResult:
    """
    Result of a biometric verification attempt.
    """
    is_verified: bool
    user_id: Optional[str] = None
    message: str = ""
    confidence: float = 0.0 # Placeholder for future
