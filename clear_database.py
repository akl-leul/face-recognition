import pickle
from utils import encrypt_data

# Clear the database - start fresh
empty_data = {
    'encodings': [],
    'names': []
}

# Save empty encrypted data
with open('authorized_faces.pkl', 'wb') as f:
    f.write(encrypt_data(empty_data))

print("✅ Database cleared - all test users removed")
print("Ready for production enrollment!")
