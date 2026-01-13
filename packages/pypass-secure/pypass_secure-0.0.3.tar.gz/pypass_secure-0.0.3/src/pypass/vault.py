import sqlite3
from pathlib import Path
from pypass.encryption import encrypt, decrypt

DB_FILE = Path("vault.db")



class VaultDB:
    def __init__(self, key: bytes):
        self.key = key
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site TEXT NOT NULL,
                username TEXT,
                password BLOB NOT NULL
            )        
        """)
        self.conn.commit()

    def add_entry (self, site, username, password):
        encrypted_pw = encrypt(password, self.key)
        self.cursor.execute(
            "INSERT INTO vault (site, username, password) VALUES (?, ?, ?)",
            (site, username, encrypted_pw)
        )
        self.conn.commit()

    def get_entries(self):
        self.cursor.execute("SELECT id, site, username, password FROM vault")
        rows = self.cursor.fetchall()

        entries = []
        for row in rows:
            entries.append({
                "id": row[0],
                "site": row[1],
                "username": row[2],
                "password": decrypt(row[3], self.key)
            })
        return entries
    
    def delete_entry(self, entry_id):
        self.cursor.execute(
            "DELETE FROM vault WHERE id = ?",
            (entry_id,)
        )
        self.conn.commit()
        print("Deleting entry id:", entry_id)

