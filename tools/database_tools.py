import sqlite3
from datetime import datetime

# We will use SQLite for simplicity as a fallback if Supabase is not configured,
# but the structure allows for easy swapping.

DB_FILE = "meetings.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS meetings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  participants TEXT,
                  start_time TEXT,
                  status TEXT,
                  created_at TEXT)''')
    conn.commit()
    conn.close()

def log_meeting(title, participants, start_time, status="Scheduled"):
    """Logs a meeting to the database."""
    init_db() # Ensure table exists
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    created_at = datetime.utcnow().isoformat()
    
    c.execute("INSERT INTO meetings (title, participants, start_time, status, created_at) VALUES (?, ?, ?, ?, ?)",
              (title, participants, start_time, status, created_at))
    
    conn.commit()
    conn.close()
    return "Meeting logged successfully."
