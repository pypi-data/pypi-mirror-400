import face_recognition
import numpy as np
import pickle
from ..errors.exceptions import FaceDetectionError, BiometricError

class BiometricEngine:
    """
    Handles face detection, encoding generation, and matching.
    """
    
    def __init__(self, tolerance=0.6, model="hog"):
        """
        Args:
            tolerance: Distance threshold for matching (lower = stricter).
            model: "hog" (CPU fast) or "cnn" (GPU accurate).
        """
        self.tolerance = tolerance
        self.model = model

    def encode_face(self, frame) -> tuple[np.ndarray, str]:
        """
        Detects and encodes a face from a BGR image (OpenCV format).
        
        Returns:
            (encoding, version_string)
            
        Raises:
            FaceDetectionError: If 0 or >1 faces are found.
        """
        # Convert BGR of OpenCV to RGB of Face Recognition
        # Ensure it is utf-8 contiguous for C++ bindings
        rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])
        
        # Detect face locations
        locations = face_recognition.face_locations(rgb_frame, model=self.model)
        
        if len(locations) == 0:
            raise FaceDetectionError("No face detected. Please ensure your face is clearly visible.")
        
        if len(locations) > 1:
            raise FaceDetectionError("Multiple faces detected. Please ensure only one person is in the frame.")
            
        # Generate encoding for the first (and only) face
        try:
            # Note: Removed explicit num_jitters=1 to rely on library defaults 
            # and avoid strict type binding mismatches in dlib 20+.
            encodings = face_recognition.face_encodings(rgb_frame, locations, model="large")
            if not encodings:
                raise FaceDetectionError("Could not encode face even though location was found.")
                
            return encodings[0], "dlib_resnet_v1"
            
        except Exception as e:
            raise BiometricError(f"Encoding failed: {str(e)}")

    def serialize_encoding(self, encoding: np.ndarray) -> bytes:
        """Serializes numpy array to bytes."""
        return pickle.dumps(encoding)

    def deserialize_encoding(self, data: bytes) -> np.ndarray:
        """Deserializes bytes to numpy array."""
        try:
            return pickle.loads(data)
        except Exception:
            raise BiometricError("Failed to deserialize encoding data.")

    def match(self, target_encoding: np.ndarray, known_encodings: list[np.ndarray]) -> bool:
        """
        Compares target encoding against a list of known encodings.
        Returns True if ANY match is found.
        """
        if not known_encodings:
            return False
            
        # matches is a list of True/False
        matches = face_recognition.compare_faces(known_encodings, target_encoding, tolerance=self.tolerance)
        return any(matches)

    def identify(self, target_encoding: np.ndarray, known_db: list[dict]) -> str | None:
        """
        Identifies the user from a list of db records.
        known_db: List of dicts {'user_id': str, 'encoding': np.ndarray}
        
        Returns: user_id or None
        """
        if not known_db:
            return None
            
        known_encodings = [rec['encoding'] for rec in known_db]
        
        # We can also use face_distance to find the BEST match
        distances = face_recognition.face_distance(known_encodings, target_encoding)
        
        best_match_index = np.argmin(distances)
        if distances[best_match_index] <= self.tolerance:
            return known_db[best_match_index]['user_id']
            
        return None
