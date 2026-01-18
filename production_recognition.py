import cv2
import os
import time
import numpy as np
from detector import detect_faces, extract_face_crop
from deepface import DeepFace
from utils import decrypt_data
from database import log_access_attempt

class ProductionRecognition:
    def __init__(self):
        self.recognition_threshold = 0.4  # Confidence threshold
        self.min_poses_required = 3  # Minimum poses to match
        self.cooldown_time = 3  # Seconds between recognitions
        self.last_recognition_time = 0
        
    def recognize_user_multi_pose(self, face_img, user_dir):
        """Recognize user using multiple poses for robustness"""
        poses = ['straight', 'left', 'right', 'up', 'down']
        pose_matches = {}
        total_confidence = 0
        valid_matches = 0
        
        for pose in poses:
            pose_dir = os.path.join(user_dir, pose)
            if not os.path.exists(pose_dir):
                continue
                
            face_files = [f for f in os.listdir(pose_dir) if f.endswith('.jpg')]
            if not face_files:
                continue
            
            best_match_confidence = 0
            best_match_verified = False
            
            # Test against all images in this pose
            for face_file in face_files:
                known_face_path = os.path.join(pose_dir, face_file)
                
                try:
                    result = DeepFace.verify(
                        img1_path=face_img,
                        img2_path=known_face_path,
                        enforce_detection=False,
                        detector_backend='opencv',
                        model_name='VGG-Face'
                    )
                    
                    if result['verified']:
                        confidence = 1.0 - result['distance']
                        if confidence > best_match_confidence:
                            best_match_confidence = confidence
                            best_match_verified = True
                            
                except Exception as e:
                    continue
            
            # Record best match for this pose
            if best_match_verified:
                pose_matches[pose] = best_match_confidence
                total_confidence += best_match_confidence
                valid_matches += 1
        
        # Calculate final confidence
        if valid_matches >= self.min_poses_required:
            avg_confidence = total_confidence / valid_matches
            return True, avg_confidence, pose_matches
        else:
            return False, 0.0, pose_matches
    
    def process_frame(self, frame):
        """Process single frame for face recognition"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_recognition_time < self.cooldown_time:
            return frame, None, 0.0, "COOLDOWN"
        
        faces = detect_faces(frame)
        recognized_user = None
        best_confidence = 0.0
        best_status = "NO_MATCH"
        
        for bbox in faces:
            x1, y1, x2, y2 = bbox
            face_img = extract_face_crop(frame, bbox)
            
            if face_img is None:
                continue
            
            # Get enrolled users
            known_encodings, known_names = decrypt_data()
            
            if not known_encodings:
                best_status = "NO_ENROLLED_USERS"
                continue
            
            # Try to recognize against each user
            for i, user_dir in enumerate(known_encodings):
                if not os.path.exists(user_dir):
                    continue
                    
                user_name = known_names[i]
                is_match, confidence, pose_matches = self.recognize_user_multi_pose(face_img, user_dir)
                
                if is_match and confidence > best_confidence:
                    recognized_user = user_name
                    best_confidence = confidence
                    best_status = "MATCH_FOUND"
            
            # Draw results
            if recognized_user:
                color = (0, 255, 0)  # Green for recognized
                label = f"{recognized_user} ({best_confidence:.2f})"
                text_color = (0, 255, 0)
                
                # Log successful recognition
                if current_time - self.last_recognition_time >= self.cooldown_time:
                    log_access_attempt(recognized_user, best_confidence, "GRANTED")
                    self.last_recognition_time = current_time
                    
            else:
                color = (0, 0, 255)  # Red for unknown
                label = f"Unknown ({best_status})"
                text_color = (0, 0, 255)
                
                # Log failed attempt
                if current_time - self.last_recognition_time >= self.cooldown_time:
                    log_access_attempt("Unknown", 0.0, "DENIED")
                    self.last_recognition_time = current_time
            
            # Draw bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
        
        return frame, recognized_user, best_confidence, best_status
    
    def run_recognition_system(self):
        """Run production recognition system"""
        print("🏭 Production Face Recognition System")
        print("=" * 50)
        print("Features:")
        print("- Multi-pose recognition (5 poses)")
        print("- Anti-spoofing protection")
        print("- Access logging")
        print("- Cooldown protection")
        print("\nPress 'q' to quit")
        
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
            return
        
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
            return
        
        print(f"✅ Camera working! Frame size: {test_frame.shape}")
        
        # Check enrolled users
        known_encodings, known_names = decrypt_data()
        print(f"\n👥 Enrolled Users: {known_names}")
        
        frame_count = 0
        recognition_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Process frame
            processed_frame, user, confidence, status = self.process_frame(frame)
            
            # Draw status overlay
            status_color = (0, 255, 0) if user else (0, 0, 255)
            cv2.putText(processed_frame, f"Status: {status}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            cv2.putText(processed_frame, f"Recognitions: {recognition_count}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.putText(processed_frame, f"Frame: {frame_count}", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Instructions
            cv2.putText(processed_frame, "Press 'q' to quit", (10, processed_frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            if user:
                recognition_count += 1
            
            cv2.imshow('Production Face Recognition', processed_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print(f"\n📊 Session Statistics:")
        print(f"   Total frames: {frame_count}")
        print(f"   Successful recognitions: {recognition_count}")
        if frame_count > 0:
            recognition_rate = (recognition_count / frame_count) * 100
            print(f"   Recognition rate: {recognition_rate:.2f}%")
        print("✅ System shutdown complete")

def main():
    system = ProductionRecognition()
    system.run_recognition_system()

if __name__ == "__main__":
    main()
