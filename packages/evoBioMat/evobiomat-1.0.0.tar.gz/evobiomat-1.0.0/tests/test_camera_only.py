import cv2
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from evobiomat.camera.capture import Webcam
    print("Successfully imported Webcam module.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

def main():
    print("=======================================")
    print("   EvoBioMat Camera Hardware Test")
    print("=======================================")
    print("This script tests ONLY the camera capture functionality.")
    print("It does NOT require the Face AI engine.")
    print("Press 'q' in the window to quit.")
    print("Opening Camera...")

    try:
        # Initialize SDK Webcam wrapper
        cam = Webcam(device_id=0)
        
        # We'll use OpenCV directly to show the stream since SDK 'capture_frame' is one-shot.
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("ERROR: Could not open webcam.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            cv2.imshow('EvoBioMat Camera Test', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        print("Camera test completed.")

    except Exception as e:
        print(f"Camera Error: {e}")

if __name__ == "__main__":
    main()
