import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# MOCK DEPENDENCIES BEFORE IMPORT because `dlib` is missing
# This allows testing the SDK logic without having the C++ libs installed
sys.modules['face_recognition'] = MagicMock()
sys.modules['face_recognition.face_locations'] = MagicMock()
sys.modules['face_recognition.face_encodings'] = MagicMock()
sys.modules['face_recognition.compare_faces'] = MagicMock()
sys.modules['face_recognition.face_distance'] = MagicMock()

sys.modules['cv2'] = MagicMock()
sys.modules['cv2.VideoCapture'] = MagicMock()

# Now we can import
from evobiomat import EvoBioMat
from evobiomat.errors.exceptions import FaceDetectionError

class TestEvoBioMat(unittest.TestCase):
    def setUp(self):
        self.mock_db_config = {'host': 'localhost', 'user': 'root', 'password': 'pw', 'database': 'db'}
        self.mock_key = b'0' * 32 # 32 bytes valid key
        
        # Patch the dependencies
        self.patcher_db = patch('evobiomat.EvoBioMat.DatabaseClient')
        self.patcher_cam = patch('evobiomat.EvoBioMat.Webcam')
        self.patcher_eng = patch('evobiomat.EvoBioMat.BiometricEngine')
        
        self.MockDB = self.patcher_db.start()
        self.MockCam = self.patcher_cam.start()
        self.MockEng = self.patcher_eng.start()
        
        self.sdk = EvoBioMat(self.mock_db_config, self.mock_key)

    def tearDown(self):
        self.patcher_db.stop()
        self.patcher_cam.stop()
        self.patcher_eng.stop()

    def test_register_success(self):
        # Setup mocks
        self.sdk.camera.capture_frame.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        self.sdk.engine.encode_face.return_value = (np.zeros(128), "v1")
        self.sdk.engine.serialize_encoding.return_value = b'serialized'
        self.sdk.db.store_biometric.return_value = True
        
        result = self.sdk.register("user1")
        self.assertTrue(result)
        self.sdk.db.store_biometric.assert_called_once()

    def test_verify_success(self):
        # Setup mocks
        self.sdk.camera.capture_frame.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        self.sdk.engine.encode_face.return_value = (np.zeros(128), "v1")
        
        # DB returns one record
        mock_rec = {'user_id': 'user1', 'face_encoding': b'encrypted_data', 'encoding_version': 'v1'}
        self.sdk.db.fetch_all_encodings.return_value = [mock_rec]
        
        # Crypto decrypt (we need to patch crypto instance on the object because it's real)
        # Or we can just let it fail if we don't patch it? 
        # The SDK init creates specific instances. We need to mock the crypto attribute.
        self.sdk.crypto = MagicMock()
        self.sdk.crypto.decrypt.return_value = b'serialized_known'
        
        self.sdk.engine.deserialize_encoding.return_value = np.zeros(128)
        self.sdk.engine.identify.return_value = "user1"
        
        result = self.sdk.verify()
        self.assertTrue(result.is_verified)
        self.assertEqual(result.user_id, "user1")

if __name__ == '__main__':
    unittest.main()