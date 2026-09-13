import sqlite3
import json
from typing import Dict, Any

class UserProfileStore:
    def __init__(self, db_path: str = "lifeledger.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id TEXT PRIMARY KEY,
                    type TEXT,
                    data TEXT,
                    confidence INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    outcome TEXT,
                    feedback TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Initialize with some default patterns for demo
            conn.execute(
                "INSERT OR IGNORE INTO patterns (id, type, data, confidence) VALUES ('electric_bill', 'bill', ?, 95)", 
                (json.dumps({"vendor": "ElectricCo", "amount_range": [80, 120]}),)
            )
            conn.execute(
                "INSERT OR IGNORE INTO patterns (id, type, data, confidence) VALUES ('dentist', 'scheduling', ?, 80)", 
                (json.dumps({"event_type": "dentist", "duration": 60}),)
            )
            
    def get_pattern(self, pattern_id: str) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data, confidence FROM patterns WHERE id = ?", (pattern_id,))
            row = cursor.fetchone()
            if row:
                data = json.loads(row[0])
                data['confidence'] = row[1]
                return data
            return None
            
    def update_confidence(self, pattern_id: str, delta: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE patterns SET confidence = confidence + ? WHERE id = ?", (delta, pattern_id))

    def log_decision(self, task_id: str, outcome: str, feedback: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO history (task_id, outcome, feedback) VALUES (?, ?, ?)", 
                (task_id, outcome, feedback)
            )
