import cv2
import time
from ..errors.exceptions import CameraError

class Webcam:
    """
    Abstractions for webcam capture using OpenCV.
    Ensures resources are released properly.
    """
    def __init__(self, device_id=0, warmup_time=2.0):
        self.device_id = device_id
        self.warmup_time = warmup_time

    def capture_frame(self):
        """
        Opens the webcam, shows a preview window, and captures a single frame
        when the user presses 'SPACE' or 'ENTER'.
        Returns:
            numpy.ndarray: The captured image frame (RGB).
        Raises:
            CameraError: If the webcam cannot be accessed.
        """
        cap = cv2.VideoCapture(self.device_id)
        if not cap.isOpened():
            raise CameraError(f"Could not access webcam (ID: {self.device_id})")

        print("  >> Press 'SPACE' to capture face, or 'q' to cancel <<")
        
        captured_frame = None
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    raise CameraError("Failed to read frame from webcam")

                # Show preview
                window_name = 'EvoBioMat - Face Capture'
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.imshow(window_name, frame)

                # Wait 1ms for key press
                key = cv2.waitKey(1) & 0xFF
                
                # Capture Logic: Space (32), Enter (13), 'c', or 's'
                if key in [32, 13, ord('c'), ord('s')]:
                    captured_frame = frame
                    print("  >> Capturing...")
                    break
                # 'q' or 'ESC' (27) to quit
                elif key in [ord('q'), 27]:
                    print("  >> Capture cancelled.")
                    break
                    
        finally:
            cap.release()
            cv2.destroyAllWindows()

        if captured_frame is None:
             raise CameraError("Capture cancelled by user.")

        # Convert BGR (OpenCV) to RGB (face_recognition)
        return cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB)

    def stream_capture(self, timeout=10):
        """
        Opens a window and waits for a face? 
        The prompt asks for "Capture live face".
        Usually, this means opening a window and letting user align face?
        Or just grabbing a frame?
        "Webcam abstraction... Fail if No face detected" implicates we just grab raw data.
        The `EvoBioMat` flow will handle the detection logic.
        This class just yields frames.
        """
        pass # Not needed for the core "capture_frame" requirement which is one-shot.
