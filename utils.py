import pickle
import numpy as np
import os
from cryptography.fernet import Fernet
from config import ENCRYPTION_KEY_FILE

def load_encryption_key():
    """Load Fernet key for encrypting face encodings"""
    return open(ENCRYPTION_KEY_FILE, 'rb').read()

def encrypt_data(data):
    """Encrypt face encodings dictionary"""
    key = load_encryption_key()
    f = Fernet(key)
    serialized = pickle.dumps(data)
    return f.encrypt(serialized)

def decrypt_data():
    """Decrypt authorized faces data from file"""
    if not os.path.exists('authorized_faces.pkl'):
        return [], []
    
    try:
        key = load_encryption_key()
        f = Fernet(key)
        with open('authorized_faces.pkl', 'rb') as file:
            encrypted_content = file.read()
        
        serialized = f.decrypt(encrypted_content)
        data = pickle.loads(serialized)
        
        # Support both old tuple and new dict formats
        if isinstance(data, dict):
            return data.get('encodings', []), data.get('names', [])
        return data  # assumed to be (encodings, names) tuple
    except Exception as e:
        print(f"⚠️ Error decrypting data: {e}. Starting with empty database.")
        return [], []

def mock_door_unlock(duration=5):
    """Simulate door unlock - replace with GPIO for production"""
    print(f"🔓 DOOR UNLOCKED for {duration} seconds (User authorized)")
    import time
    time.sleep(duration)
    print("🔒 DOOR LOCKED")
