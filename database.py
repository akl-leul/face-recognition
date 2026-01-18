import sqlite3
import os
from datetime import datetime

def init_attendance_db():
    """Initialize attendance database"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Create attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            decision TEXT NOT NULL,
            confidence REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'STANDALONE'
        )
    ''')
    
    conn.commit()
    conn.close()
    print("📊 Attendance database initialized: attendance.db")

def log_attendance(user_name, confidence, decision, source='STANDALONE'):
    """Log attendance record"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO attendance (user_name, decision, confidence, source, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_name, decision, confidence, source, datetime.now()))
    
    conn.commit()
    conn.close()

def get_attendance_records(limit=100):
    """Get attendance records"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_name, decision, confidence, timestamp, source
        FROM attendance 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    records = cursor.fetchall()
    conn.close()
    
    # Convert to list of dictionaries
    columns = ['user_name', 'decision', 'confidence', 'timestamp', 'source']
    return [dict(zip(columns, record)) for record in records]

def get_attendance_stats():
    """Get attendance statistics"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Today's stats
    today = datetime.now().date()
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN decision = 'GRANTED' THEN 1 ELSE 0 END) as granted,
            SUM(CASE WHEN decision = 'DENIED' THEN 1 ELSE 0 END) as denied
        FROM attendance 
        WHERE DATE(timestamp) = ?
    ''', (today,))
    
    today_stats = cursor.fetchone()
    
    # Overall stats
    cursor.execute('''
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT user_name) as unique_users
        FROM attendance
    ''')
    
    overall_stats = cursor.fetchone()
    conn.close()
    
    return {
        'today': {
            'total': today_stats[0] or 0,
            'granted': today_stats[1] or 0,
            'denied': today_stats[2] or 0
        },
        'overall': {
            'total_records': overall_stats[0] or 0,
            'unique_users': overall_stats[1] or 0
        }
    }

def cleanup_old_records(days=30):
    """Remove attendance records older than specified days"""
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM attendance 
        WHERE timestamp < datetime('now', '-{} days')
    ''', (days,))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted_count

# Legacy functions for backward compatibility
def init_db():
    """Initialize the access logs database"""
    conn = sqlite3.connect('access_logs.db')
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS access_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            identity TEXT NOT NULL,
            confidence REAL,
            decision TEXT NOT NULL,
            spoof_score REAL DEFAULT 0,
            image_path TEXT
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON access_logs(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_identity ON access_logs(identity)')
    
    conn.commit()
    conn.close()
    print(f"📊 Database initialized: access_logs.db")

def log_access_attempt(identity, confidence, decision, spoof_score=0.0, image_path=None):
    """Log every access attempt"""
    conn = sqlite3.connect('access_logs.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO access_logs 
        (timestamp, identity, confidence, decision, spoof_score, image_path)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), identity, confidence, decision, spoof_score, image_path))
    
    conn.commit()
    conn.close()

# Initialize on import
init_attendance_db()
