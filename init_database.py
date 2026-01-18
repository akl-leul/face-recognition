import pickle
import os
from utils import encrypt_data, load_encryption_key
from cryptography.fernet import Fernet

# Production setup script
def initialize_production():
    """Setup a clean database for production"""
    empty_data = {
        'encodings': [],
        'names': []
    }
    
    # Save empty encrypted data
    with open('authorized_faces.pkl', 'wb') as f:
        f.write(encrypt_data(empty_data))
    
    # Initialize SQLite databases
    from database import init_attendance_db, init_db
    init_attendance_db()
    init_db()
    
    print("\n🚀 Production System Ready!")
    print("--------------------------")
    print("✅ face database (authorized_faces.pkl) initialized and empty.")
    print("✅ attendance database (attendance.db) initialized.")
    print("✅ log database (access_logs.db) initialized.")
    print("\nYou can now start 'web_app.py' and begin enrolling users.")

if __name__ == "__main__":
    initialize_production()
