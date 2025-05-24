import sqlite3
from datetime import datetime
from models.note import Note

class NoteManager:
    def __init__(self, db_path="notes.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS notes
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     title TEXT NOT NULL,
                     content TEXT,
                     category TEXT,
                     created_at TIMESTAMP)''')
        conn.commit()
        conn.close()

    def add_note(self, note):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO notes 
                    (title, content, category, created_at) 
                    VALUES (?, ?, ?, ?)""",
                 (note.title, note.content, note.category, 
                  note.created_at))
        conn.commit()
        conn.close()

    def get_all_notes(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM notes ORDER BY created_at DESC")
        notes = c.fetchall()
        conn.close()
        return notes

    def get_note_by_id(self, note_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM notes WHERE id=?", (note_id,))
        note = c.fetchone()
        conn.close()
        return note

    def update_note(self, note_id, title, content, category):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""UPDATE notes 
                    SET title = ?, content = ?, category = ? 
                    WHERE id = ?""",
                 (title, content, category, note_id))
        conn.commit()
        conn.close()

    def delete_note(self, note_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
        conn.close()