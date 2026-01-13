class EvoBioMatError(Exception):
    """Base exception for EvoBioMat SDK."""
    pass

class FaceDetectionError(EvoBioMatError):
    """Raised when face detection fails (0 or >1 faces)."""
    pass

class BiometricError(EvoBioMatError):
    """Raised when biometric encoding or processing fails."""
    pass

class DatabaseError(EvoBioMatError):
    """Raised when database operations fail."""
    pass

class SecurityError(EvoBioMatError):
    """Raised when encryption/decryption or key issues occur."""
    pass

class ConfigurationError(EvoBioMatError):
    """Raised when SDK configuration (e.g., db_config) is invalid."""
    pass

class CameraError(EvoBioMatError):
    """Raised when webcam access or frame capture fails."""
    pass
