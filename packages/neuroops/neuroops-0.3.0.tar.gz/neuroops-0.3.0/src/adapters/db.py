import sqlite3
import os
import json
from datetime import datetime

class LocalDBAdapter:
    """
    Handles persistence for User Comments using SQLite.
    Restored from JSON to support concurrency and future SQL migration.
    """
    def __init__(self, db_path="neuroops.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Creates the table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Schema: ID, File_ID (A+B name), User, Comment, Context (Slice/Time), Timestamp
        c.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id TEXT NOT NULL,
                user TEXT DEFAULT 'Anonymous',
                comment TEXT NOT NULL,
                context_info TEXT,  
                created_at TIMESTAMP
            )
        ''')
        # Schema: File_ID, Status (Pending/Approved/Changes Requested), Updated_At
        c.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                file_id TEXT PRIMARY KEY,
                status TEXT DEFAULT 'Pending',
                updated_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def set_review_status(self, file_id, status):
        """Updates the review status for a file pair."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO reviews (file_id, status, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(file_id) DO UPDATE SET
                status=excluded.status,
                updated_at=excluded.updated_at
        ''', (file_id, status, datetime.now()))
        conn.commit()
        conn.close()

    def get_review_status(self, file_id):
        """Returns the current status string."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT status FROM reviews WHERE file_id = ?', (file_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else "Pending"

    def add_comment(self, file_id, comment, context_info, user="Researcher"):
        """
        Adds a comment with context (JSON string).
        context_info: dict containing view state (e.g. {'slice': 50, 'plane': 'Axial'})
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Serialize context to JSON for storage
        context_json = json.dumps(context_info)
        
        c.execute('''
            INSERT INTO comments (file_id, user, comment, context_info, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_id, user, comment, context_json, datetime.now()))
        conn.commit()
        conn.close()

    def get_comments(self, file_id):
        """
        Returns list of dicts: [{'user':..., 'comment':..., 'context':..., 'time':...}]
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT user, comment, context_info, created_at FROM comments WHERE file_id = ? ORDER BY created_at DESC', (file_id,))
        rows = c.fetchall()
        conn.close()
        
        comments = []
        for r in rows:
            try:
                ctx = json.loads(r[2])
            except:
                ctx = {}
                
            comments.append({
                'user': r[0],
                'comment': r[1],
                'context': ctx,
                'created_at': r[3]
            })
            
        return comments