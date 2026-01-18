import cv2
import os
import time
import numpy as np
from detector import detect_faces, extract_face_crop
from utils import encrypt_data
import pickle

class ProductionEnrollment:
    def __init__(self):
        self.enrollment_poses = ['straight', 'left', 'right', 'up', 'down']
        self.current_pose_index = 0
        self.captured_faces = {}
        self.min_faces_per_pose = 1
        self.max_faces_per_pose = 1
        self.current_captures = 0
        
    def get_pose_instructions(self):
        """Get instructions for current pose"""
        instructions = {
            'straight': "Look straight at camera",
            'left': "Turn your head slightly to the LEFT",
            'right': "Turn your head slightly to the RIGHT", 
            'up': "Tilt your head slightly UP",
            'down': "Tilt your head slightly DOWN"
        }
        return instructions.get(self.enrollment_poses[self.current_pose_index], "Unknown pose")
    
    def save_face_images(self, name, face_images):
        """Save face images in organized structure"""
        user_dir = f"known_faces/{name}"
        os.makedirs(user_dir, exist_ok=True)
        
        # Save each pose in separate subdirectory
        for pose, images in face_images.items():
            pose_dir = os.path.join(user_dir, pose)
            os.makedirs(pose_dir, exist_ok=True)
            
            for i, img in enumerate(images):
                filename = f"{pose}_{i}.jpg"
                filepath = os.path.join(pose_dir, filename)
                cv2.imwrite(filepath, img)
                print(f"  Saved: {filename}")
    
    def update_encrypted_data(self, name):
        """Update encrypted user database"""
        try:
            with open('authorized_faces.pkl', 'rb') as f:
                key = open('key.key', 'rb').read()
                from cryptography.fernet import Fernet
                fernet = Fernet(key)
                encrypted = f.read()
                decrypted = fernet.decrypt(encrypted)
                data = pickle.loads(decrypted)
        except:
            data = {'encodings': [], 'names': []}
        
        # Add new user
        user_dir = f"known_faces/{name}"
        data['encodings'].append(user_dir)
        data['names'].append(name)
        
        # Save back encrypted
        with open('authorized_faces.pkl', 'wb') as f:
            f.write(encrypt_data(data))
    
    def enroll_user(self, name):
        """Complete enrollment process with multiple poses"""
        print(f"🎯 Production Enrollment: {name}")
        print("=" * 50)
        print("This will automatically capture 5 poses:")
        print("1. Straight - Look directly at camera")
        print("2. Left - Turn head slightly left") 
        print("3. Right - Turn head slightly right")
        print("4. Up - Tilt head slightly up")
        print("5. Down - Tilt head slightly down")
        print("\nGet ready! Starting in 3 seconds...")
        
        # Try different camera backends
        cap = None
        camera_indices = [0, 1, 2]  # Try multiple camera indices
        
        for idx in camera_indices:
            print(f"Trying camera {idx}...")
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)  # Use DirectShow on Windows
            if cap.isOpened():
                print(f"✅ Camera {idx} opened successfully")
                break
            else:
                cap.release()
                cap = None
        
        if cap is None or not cap.isOpened():
            print("❌ Could not open any camera")
            print("Please check:")
            print("- Camera is connected")
            print("- Camera is not being used by another application")
            print("- Camera drivers are installed")
            return False
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Test camera
        print("Testing camera...")
        ret, test_frame = cap.read()
        if not ret or test_frame is None:
            print("❌ Camera test failed")
            cap.release()
            return False
        
        print(f"✅ Camera working! Frame size: {test_frame.shape}")
        
        # Countdown before starting
        for i in range(3, 0, -1):
            print(f"Starting in {i}...")
            time.sleep(1)
        
        face_images = {}
        
        # Auto-capture all poses with manual control
        for pose_index, current_pose in enumerate(self.enrollment_poses):
            print(f"\n📸 Capturing {current_pose.upper()} pose...")
            
            # Initialize pose capture
            face_images[current_pose] = []
            captured = False
            
            # Keep trying until user captures or cancels
            while not captured:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                faces = detect_faces(frame)
                
                # Draw UI
                cv2.putText(frame, f"Pose {pose_index + 1}/5: {current_pose.upper()}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                
                cv2.putText(frame, self.get_pose_instructions(), (10, 70), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                cv2.putText(frame, f"Captured: {len(face_images[current_pose])}/1", (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.putText(frame, "SPACE = Capture | ESC = Cancel", (10, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Process detected faces
                for bbox in faces:
                    x1, y1, x2, y2 = bbox
                    face_img = extract_face_crop(frame, bbox)
                    
                    if len(face_images[current_pose]) >= self.max_faces_per_pose:
                        # Already captured - show success
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                        cv2.putText(frame, "✅ CAPTURED!", (x1, y1-30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    else:
                        # Draw face rectangle for potential capture
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
                
                cv2.imshow('Production Enrollment', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    print("❌ Enrollment cancelled")
                    cap.release()
                    cv2.destroyAllWindows()
                    return False
                elif key == 32:  # SPACE
                    # Try to capture current frame
                    if faces:
                        for bbox in faces:
                            x1, y1, x2, y2 = bbox
                            face_img = extract_face_crop(frame, bbox)
                            
                            if face_img is not None:
                                face_images[current_pose].append(face_img.copy())
                                print(f"  ✅ Captured {current_pose} pose!")
                                captured = True
                                break
                    
                    if not captured:
                        print("  ❌ No face detected. Try again.")
                
                time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            
            if not captured:
                print(f"❌ Failed to capture {current_pose} pose")
                cap.release()
                cv2.destroyAllWindows()
                return False
        
        # Save all captured faces
        print(f"\n💾 Saving enrollment data for {name}...")
        self.save_face_images(name, face_images)
        self.update_encrypted_data(name)
        
        total_faces = sum(len(images) for images in face_images.values())
        print(f"✅ Enrollment complete!")
        print(f"   Total captures: {total_faces}")
        print(f"   Poses: {list(face_images.keys())}")
        
        cap.release()
        cv2.destroyAllWindows()
        return True

def main():
    print("🏭 Production Face Enrollment System")
    print("This system captures 5 different poses for robust recognition")
    print()
    
    name = input("Enter user name: ").strip()
    if not name:
        print("❌ Name cannot be empty")
        return
    
    enrollment = ProductionEnrollment()
    success = enrollment.enroll_user(name)
    
    if success:
        print(f"\n🎉 User '{name}' successfully enrolled!")
        print("You can now use the production recognition system.")

if __name__ == "__main__":
    main()
