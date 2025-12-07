import sqlite3
import json
from datetime import datetime
import os

DB_PATH = 'conversations.db'

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            model_id TEXT NOT NULL,
            session_id TEXT,
            feedback INTEGER DEFAULT 0,
            used_for_training INTEGER DEFAULT 0
        )
    ''')
    
    # Create training_queue table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            added_at TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            conversation_count INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def save_conversation(user_message, ai_response, model_id, session_id=None):
    """Save a conversation to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO conversations (timestamp, user_message, ai_response, model_id, session_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), user_message, ai_response, model_id, session_id))
    
    conn.commit()
    conn.close()

def get_recent_conversations(limit=100):
    """Get recent conversations for retraining"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT user_message, ai_response 
        FROM conversations 
        WHERE used_for_training = 0
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    conversations = cursor.fetchall()
    conn.close()
    
    return conversations

def mark_conversations_trained():
    """Mark conversations as used for training"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('UPDATE conversations SET used_for_training = 1 WHERE used_for_training = 0')
    
    conn.commit()
    conn.close()

def get_conversation_stats():
    """Get statistics about conversations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM conversations')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM conversations WHERE used_for_training = 0')
    pending = cursor.fetchone()[0]
    
    conn.close()
    
    return {'total': total, 'pending_training': pending}

def export_training_data():
    """Export conversations as training data"""
    conversations = get_recent_conversations(limit=1000)
    
    training_data = []
    for user_msg, ai_resp in conversations:
        training_data.append({
            "instruction": user_msg,
            "input": "",
            "output": ai_resp
        })
    
    # Save to file
    filename = f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join('data', 'auto_generated', filename)
    
    os.makedirs(os.path.join('data', 'auto_generated'), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)
    
    return filepath

# Initialize database on import
init_db()