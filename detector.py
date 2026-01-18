import cv2
import numpy as np

# Initialize OpenCV face detector once
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def init_face_detector():
    """Initialize OpenCV face detector"""
    global face_cascade
    if face_cascade.empty():
        print("Warning: Could not load face cascade classifier")
        return None
    return face_cascade

def detect_faces(frame):
    """Detect faces in frame and return bounding boxes"""
    global face_cascade
    if face_cascade.empty():
        face_cascade = init_face_detector()
        if face_cascade.empty():
            return []
    
    # Convert to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces with more lenient parameters
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,  # Was 1.1 - more sensitive
        minNeighbors=3,      # Was 5 - more lenient
        minSize=(20, 20),   # Was 30x30 - smaller minimum
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Convert to (x1, y1, x2, y2) format
    face_boxes = []
    for (x, y, w, h) in faces:
        face_boxes.append((x, y, x + w, y + h))
    
    return face_boxes

def extract_face_crop(frame, bbox):
    """Extract and preprocess face region"""
    x1, y1, x2, y2 = bbox
    # Add padding and ensure bounds
    h, w = frame.shape[:2]
    x1 = max(0, x1 - 10)
    y1 = max(0, y1 - 10)
    x2 = min(w, x2 + 10)
    y2 = min(h, y2 + 10)
    
    face = frame[y1:y2, x1:x2]
    if face.size == 0:
        return None
    
    # Resize to standard 160x160 for recognition
    face = cv2.resize(face, (160, 160))
    return face
