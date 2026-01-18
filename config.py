import os

# System configuration
CAMERA_ID = 0
DETECTION_CONFIDENCE = 0.7
RECOGNITION_TOLERANCE = 0.6  # 0.5-0.7 range
LIVENESS_THRESHOLD = 0.8

# File paths (generated automatically)
AUTHORIZED_FACES_FILE = 'authorized_faces.pkl'
ENCRYPTION_KEY_FILE = 'key.key'
DATABASE_FILE = 'access_logs.db'

# Generate encryption key if missing
if not os.path.exists(ENCRYPTION_KEY_FILE):
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    with open(ENCRYPTION_KEY_FILE, 'wb') as f:
        f.write(key)
