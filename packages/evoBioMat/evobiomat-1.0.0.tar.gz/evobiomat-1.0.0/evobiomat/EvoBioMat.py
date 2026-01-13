from .database.client import DatabaseClient
from .security.crypto import BiometricEncryption
from .camera.capture import Webcam
from .biometric.engine import BiometricEngine
from .api.types import VerificationResult
from .errors.exceptions import EvoBioMatError, ConfigurationError

class EvoBioMat:
    """
    Main entry point for EvoBioMat SDK.
    """

    def __init__(self, db_config: dict, encryption_key: str | bytes, camera_id=0):
        """
        Initialize the SDK.

        Args:
            db_config (dict): MySQL configuration {'host', 'user', 'password', 'database'}.
            encryption_key (str|bytes): 32-byte AES key (or base64 encoded).
            camera_id (int): ID of the webcam device (default 0).
        """
        try:
            self.db = DatabaseClient(db_config)
            self.crypto = BiometricEncryption(encryption_key)
            self.camera = Webcam(device_id=camera_id)
            self.engine = BiometricEngine()
        except Exception as e:
            if isinstance(e, EvoBioMatError):
                raise
            raise ConfigurationError(f"SDK Initialization failed: {e}")

    def register(self, user_id: str) -> bool:
        """
        Capture face and register user with the given ID.
        
        Args:
            user_id (str): Unique identifier for the user.
        
        Returns:
            bool: True if successful.
            
        Raises:
            EvoBioMatError: On specific failures (Face not found, DB error, etc).
        """
        # 1. Capture
        frame = self.camera.capture_frame()
        
        # 2. Encode
        encoding, version = self.engine.encode_face(frame)
        
        # 3. Serialize & Encrypt
        raw_bytes = self.engine.serialize_encoding(encoding)
        encrypted_data = self.crypto.encrypt(raw_bytes)
        
        # 4. Store
        return self.db.store_biometric(user_id, encrypted_data, version)

    def verify(self) -> VerificationResult:
        """
        Capture face and verify against stored biometrics.
        
        Returns:
            VerificationResult
        """
        try:
            # 1. Capture
            frame = self.camera.capture_frame()
            
            # 2. Encode target
            target_encoding, _ = self.engine.encode_face(frame)
            
            # 3. Fetch all (In a real enterprise system with millions of users, 
            # we would not fetch all. We would likely require a claimed ID to 1:1 match
            # or use vector search at DB level. For this SDK constraints: "Match against stored encodings".
            # We will fetch all.
            records = self.db.fetch_all_encodings()
            
            if not records:
                return VerificationResult(is_verified=False, message="No users registered in database.")
                
            # 4. Decrypt and prepare known list
            # Optimize: Decrypting ALL rows every time is slow.
            # Production Grade: Cache decrypted encodings in memory or Redis.
            # For this SDK: We will decrypt on fly.
            known_db = []
            for record in records:
                try:
                    decrypted_bytes = self.crypto.decrypt(record['face_encoding'])
                    kf_encoding = self.engine.deserialize_encoding(decrypted_bytes)
                    known_db.append({'user_id': record['user_id'], 'encoding': kf_encoding})
                except Exception:
                    # Skip corrupted/un-decryptable records (e.g. key rotation issues)
                    continue
            
            # 5. Identify
            match_user_id = self.engine.identify(target_encoding, known_db)
            
            if match_user_id:
                return VerificationResult(is_verified=True, user_id=match_user_id, message="Verified")
            else:
                return VerificationResult(is_verified=False, message="Face not found in database.")
                
        except EvoBioMatError as e:
            # Wrap known errors in a failed result? Or raise?
            # "Clear SDK-level exceptions" required. 
            # "Return typed result" required for Verify.
            # If camera fails, we should probably raise so app knows HW is broken.
            # If no face detected, we should probably return Not Verified? 
            # Specification says: "Fail if: No face detected ... Clear SDK-level exceptions"
            # So verify() should probably RAISE FaceDetectionError if no face.
            raise e
