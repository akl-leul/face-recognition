import cv2
import sys

def test_cameras():
    """Test available camera indices"""
    print("Testing available cameras...")
    
    available_cameras = []
    
    for i in range(5):  # Test indices 0-4
        print(f"\nTesting camera index {i}...")
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            
            if cap.isOpened():
                # Try to read a frame
                ret, frame = cap.read()
                if ret:
                    print(f"✅ Camera {i}: SUCCESS - Frame size: {frame.shape}")
                    available_cameras.append(i)
                else:
                    print(f"❌ Camera {i}: Can't read frame")
                cap.release()
            else:
                print(f"❌ Camera {i}: Cannot open")
                
        except Exception as e:
            print(f"❌ Camera {i}: Error - {e}")
    
    if available_cameras:
        print(f"\n✅ Found working cameras: {available_cameras}")
        print("You can use these camera indices in the application.")
    else:
        print("\n❌ No working cameras found!")
        print("\nPossible solutions:")
        print("1. Connect a camera to your computer")
        print("2. Close other applications that might be using the camera (Zoom, Teams, etc.)")
        print("3. Check camera permissions in Windows settings")
        print("4. Restart your computer")
        print("5. Try using a different camera or USB port")

if __name__ == "__main__":
    test_cameras()
    input("\nPress Enter to exit...")
