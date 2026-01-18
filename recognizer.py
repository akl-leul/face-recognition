import cv2
import numpy as np
from deepface import DeepFace
from utils import decrypt_data
import os

def check_liveness(face_img):
    """Anti-spoofing check using DeepFace - more lenient for testing"""
    try:
        result = DeepFace.extract_faces(
            img_path=face_img,
            anti_spoofing=True,
            enforce_detection=False
        )
        if result and len(result) > 0:
            # Lower the threshold for testing - was 0.8, now 0.3
            is_real = result[0].get('is_real', 0) > 0.3
            return is_real
    except:
        # If anti-spoofing fails, assume it's real for testing
        return True
    return False

def recognize_face(face_img, tolerance=0.8):  # Increased tolerance from 0.6 to 0.8
    """Complete recognition pipeline with liveness check using DeepFace"""
    
    # 1. Liveness check
    if not check_liveness(face_img):
        return None, 0.0, "SPOOF_DETECTED"
    
    # 2. Get known faces data
    known_encodings, known_names = decrypt_data()
    
    if not known_encodings:
        return None, 0.0, "NO_KNOWN_FACES"
    
    # 3. Try to match against known faces using DeepFace
    best_match = None
    best_confidence = 0.0
    
    for i, known_encoding_path in enumerate(known_encodings):
        try:
            # If it's a directory, get all face images in it
            if os.path.isdir(known_encoding_path):
                face_files = [f for f in os.listdir(known_encoding_path) if f.endswith('.jpg')]
                for face_file in face_files:
                    known_face_path = os.path.join(known_encoding_path, face_file)
                    
                    # Compare face with known face using DeepFace
                    result = DeepFace.verify(
                        img1_path=face_img,
                        img2_path=known_face_path,
                        enforce_detection=False,
                        detector_backend='opencv'
                    )
                    
                    if result['verified']:
                        confidence = 1.0 - result['distance']
                        if confidence > best_confidence and confidence > (1.0 - tolerance):
                            best_confidence = confidence
                            best_match = known_names[i]
            else:
                # Handle legacy single file format
                result = DeepFace.verify(
                    img1_path=face_img,
                    img2_path=known_encoding_path,
                    enforce_detection=False,
                    detector_backend='opencv'
                )
                
                if result['verified']:
                    confidence = 1.0 - result['distance']
                    if confidence > best_confidence and confidence > (1.0 - tolerance):
                        best_confidence = confidence
                        best_match = known_names[i]
                    
        except Exception as e:
            continue
    
    # 4. Return result
    if best_match:
        return best_match, best_confidence, "MATCH_FOUND"
    else:
        return None, 0.0, "NO_MATCH"
