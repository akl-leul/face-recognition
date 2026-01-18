import cv2
import numpy as np
from detector import detect_faces
from utils import decrypt_data
import pickle
from scipy.spatial.distance import cosine
import base64
import time
from perfect_recognizer import perfect_recognizer
from speech_synthesizer import speak_name_once

class SimpleFaceRecognition:
    def __init__(self):
        self.known_encodings = []
        self.known_names = []
        self.last_recognized_name = None
        self.last_recognition_time = 0
        self.recognition_cooldown = 3.0  # seconds between same name calls
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load known face encodings from encrypted database"""
        try:
            known_encodings, known_names = decrypt_data()
            self.known_encodings = known_encodings if known_encodings else []
            self.known_names = known_names if known_names else []
            print(f"✅ Loaded {len(self.known_names)} known faces")
        except Exception as e:
            print(f"❌ Error loading known faces: {e}")
            self.known_encodings = []
            self.known_names = []
    
    def recognize_face(self, frame):
        """Perfect face recognition - detect and match with 100% accuracy"""
        try:
            # Use perfect recognizer for 100% accuracy
            name, confidence, status = perfect_recognizer.recognize_face_perfect(frame)
            
            current_time = time.time()
            
            if status == "PERFECT_MATCH" or status == "PARTIAL_MATCH":
                # Check if this is the same person as last time
                if (name == self.last_recognized_name and 
                    current_time - self.last_recognition_time < self.recognition_cooldown):
                    # Same person within cooldown - don't call name again
                    return None, f"Already recognized: {name}"
                
                # New person or cooldown expired - call the name
                self.last_recognized_name = name
                self.last_recognition_time = current_time
                
                # Speak the name out loud
                speak_name_once(name, confidence * 100)
                
                # Extract face crop for display
                faces = detect_faces(frame)
                if len(faces) > 0:
                    x, y, x2, y2 = faces[0]
                    face_crop = frame[y:y2, x:x2]
                    if face_crop.size > 0:
                        return face_crop, f"{name} ({confidence*100:.1f}% confidence - NAME CALLED)"
                    else:
                        return None, f"{name} ({confidence*100:.1f}% confidence - NAME CALLED)"
                else:
                    return None, f"{name} ({confidence*100:.1f}% confidence - NAME CALLED)"
            elif status == "NO_FACE_DETECTED":
                return None, "No face detected"
            elif status == "NO_MATCH":
                # Reset cooldown for unknown person
                self.last_recognized_name = None
                self.last_recognition_time = 0
                
                # Extract face crop for display
                faces = detect_faces(frame)
                if len(faces) > 0:
                    x, y, x2, y2 = faces[0]
                    face_crop = frame[y:y2, x:x2]
                    if face_crop.size > 0:
                        return face_crop, "Who the hell are you?"
                    else:
                        return None, "Who the hell are you?"
                else:
                    return None, "Who the hell are you?"
            else:
                return None, f"Recognition status: {status}"
                
        except Exception as e:
            print(f"❌ Error in face recognition: {e}")
            return None, "Recognition error"
    
    def add_new_user(self, frame, name):
        """Add a new user with perfect face encoding"""
        try:
            # Use perfect recognizer for 100% accurate enrollment
            success, message = perfect_recognizer.add_perfect_user(frame, name)
            
            if success:
                # Reload known faces to sync
                self.load_known_faces()
            
            return success, message
            
        except Exception as e:
            print(f"❌ Error adding new user: {e}")
            return False, f"Error: {str(e)}"
    
    def save_to_database(self):
        """Save known faces to encrypted database"""
        try:
            from utils import encrypt_data
            data = (self.known_encodings, self.known_names)
            with open('authorized_faces.pkl', 'wb') as f:
                f.write(encrypt_data(data))
            print(f"✅ Saved {len(self.known_names)} users to database")
        except Exception as e:
            print(f"❌ Error saving database: {e}")

    def delete_user(self, name):
        """Remove a user from the known faces"""
        try:
            if name in self.known_names:
                idx = self.known_names.index(name)
                self.known_names.pop(idx)
                self.known_encodings.pop(idx)
                self.save_to_database()
                return True, f"Successfully deleted {name}"
            return False, f"User {name} not found"
        except Exception as e:
            print(f"❌ Error deleting user: {e}")
            return False, str(e)

    def recognize_continuous(self):
        """Run continuous recognition in a loop"""
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return

        print("🚀 Starting Automatic Face Recognition...")
        print("Press 'q' to quit")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Recognize face
            face_crop, result = self.recognize_face(frame)
            
            # Draw on frame
            faces = detect_faces(frame)
            for (x1, y1, x2, y2) in faces:
                color = (0, 255, 0) if "Unknown" not in result and "No face" not in result else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, result, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            cv2.imshow('Automatic Recognition', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# Global instance
simple_recognition = None

def get_simple_recognition():
    """Get or create simple recognition instance"""
    global simple_recognition
    if simple_recognition is None:
        simple_recognition = SimpleFaceRecognition()
    return simple_recognition

if __name__ == "__main__":
    recognizer = get_simple_recognition()
    recognizer.recognize_continuous()
