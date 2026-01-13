import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from ..errors.exceptions import SecurityError

class BiometricEncryption:
    """
    Handles secure AES-256 encryption/decryption of biometric data.
    Uses AES-GCM (Galois/Counter Mode) for authenticated encryption.
    """

    def __init__(self, key: str | bytes):
        """
        Initialize with a 256-bit (32 byte) key.
        
        Args:
            key: 32-byte key as bytes or base64 encoded string.
        """
        try:
            if isinstance(key, str):
                # Attempt to decode if it looks like base64
                if len(key) == 44 and key.endswith('='):
                    self.key = base64.urlsafe_b64decode(key)
                else:
                    self.key = key.encode('utf-8')
            elif isinstance(key, bytes) and len(key) == 44:
                 # Handle standard Fernet.generate_key() output (bytes, base64 encoded)
                 try:
                     self.key = base64.urlsafe_b64decode(key)
                 except Exception:
                     self.key = key
            else:
                self.key = key
            
            if len(self.key) != 32:
                 raise SecurityError(f"Encryption key must be exactly 32 bytes (256 bits). Provided: {len(self.key)} bytes.")
                 
        except Exception as e:
             raise SecurityError(f"Invalid encryption key: {str(e)}")

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypts data using AES-256-GCM.
        Returns: IV + TAG + CIPHERTEXT combined.
        """
        try:
            # Generate a 12-byte IV (96 bits) as recommended for GCM
            iv = os.urandom(12)
            
            encryptor = Cipher(
                algorithms.AES(self.key),
                modes.GCM(iv)
            ).encryptor()
            
            ciphertext = encryptor.update(plaintext) + encryptor.finalize()
            
            # Return IV + TAG + Ciphertext so we can decrypt later
            # Structure: [IV (12)] + [TAG (16)] + [Ciphertext (N)]
            return iv + encryptor.tag + ciphertext
            
        except Exception as e:
            raise SecurityError(f"Encryption failed: {str(e)}")

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypts data using AES-256-GCM.
        Expects: IV (12) + TAG (16) + CIPHERTEXT.
        """
        try:
            if len(data) < 28: # 12 (IV) + 16 (Tag)
                raise SecurityError("Invalid data format for decryption.")
                
            iv = data[:12]
            tag = data[12:28]
            ciphertext = data[28:]
            
            decryptor = Cipher(
                algorithms.AES(self.key),
                modes.GCM(iv, tag)
            ).decryptor()
            
            return decryptor.update(ciphertext) + decryptor.finalize()
            
        except Exception as e:
            raise SecurityError(f"Decryption failed: {str(e)}")
