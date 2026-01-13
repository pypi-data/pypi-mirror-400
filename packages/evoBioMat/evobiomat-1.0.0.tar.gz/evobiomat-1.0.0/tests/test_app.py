import os
import sys
import cryptography.fernet

# Add project root to path so we can run without installing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from evobiomat import EvoBioMat
    from evobiomat.errors.exceptions import EvoBioMatError
except ImportError as e:
    print("CRITICAL ERROR: Could not import 'evobiomat'.")
    print(f"Details: {e}")
    print("Please ensure 'dlib' and 'face_recognition' are installed correctly.")
    print("On Windows, you may need to install CMake first: https://cmake.org/download/")
    sys.exit(1)

def main():
    print("=======================================")
    print("   EvoBioMat Consumer Test App")
    print("=======================================")
    
    # 1. Config
    host = input("MySQL Host [localhost]: ") or "localhost"
    user = input("MySQL User [root]: ") or "root"
    password = input("MySQL Password: ")
    database = input("MySQL Database [evobiomat_test]: ") or "evobiomat_test"
    
    db_config = {"host": host, "user": user, "password": password, "database": database}
    
    # 2. Key (In production, load this from env!)
    print("\n[Security] Generating Session Key...")
    key = cryptography.fernet.Fernet.generate_key()
    
    try:
        # 3. Init
        print("Initializing SDK...")
        bio = EvoBioMat(db_config, key)
        print(">> SDK Initialized.")

        # 4. Interactive Loop
        while True:
            print("\nCOMMANDS:")
            print("  [r] Register Setup (Face Scan)")
            print("  [v] Verify (Face Scan)")
            print("  [q] Quit")
            
            cmd = input("Select: ").lower().strip()
            
            if cmd == 'r':
                uid = input("  Enter New User ID: ")
                print("  >> LOOK AT WEBCAM NOW <<")
                try:
                    bio.register(uid)
                    print(f"  [SUCCESS] User '{uid}' registered.")
                except Exception as e:
                    print(f"  [FAILED] Registration error: {e}")
                    
            elif cmd == 'v':
                print("  >> LOOK AT WEBCAM NOW <<")
                try:
                    res = bio.verify()
                    if res.is_verified:
                        print(f"  [MATCH] Verified User: {res.user_id}")
                    else:
                        print(f"  [DENIED] {res.message}")
                except Exception as e:
                    print(f"  [ERROR] Verification error: {e}")
                    
            elif cmd == 'q':
                print("Exiting.")
                break
                
    except Exception as e:
        print(f"App Crash: {e}")

if __name__ == "__main__":
    main()
