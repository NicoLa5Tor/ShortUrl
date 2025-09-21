import sqlite3
import os
from typing import Optional, List, Dict
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = "shorturl.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database and create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_url(self, code: str, original_url: str) -> bool:
        """Save a URL mapping to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO urls (code, original_url) VALUES (?, ?)",
                    (code, original_url)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_url(self, code: str) -> Optional[str]:
        """Get the original URL by code"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT original_url FROM urls WHERE code = ?",
                (code,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def code_exists(self, code: str) -> bool:
        """Check if a code already exists"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM urls WHERE code = ?",
                (code,)
            )
            return cursor.fetchone() is not None

    def get_url_details(self, code: str) -> Optional[Dict]:
        """Get detailed information about a URL by code"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, code, original_url, created_at FROM urls WHERE code = ?",
                (code,)
            )
            result = cursor.fetchone()
            return dict(result) if result else None

    def get_all_urls(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all URLs from the database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT id, code, original_url, created_at FROM urls ORDER BY created_at DESC"
            if limit:
                query += f" LIMIT {limit}"
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def delete_url(self, code: str) -> bool:
        """Delete a specific URL by code"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM urls WHERE code = ?",
                (code,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_all_urls(self) -> int:
        """Delete all URLs from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM urls")
            conn.commit()
            return cursor.rowcount

    def get_stats(self) -> Dict:
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) as total FROM urls")
            total = cursor.fetchone()[0]

            cursor = conn.execute(
                "SELECT created_at FROM urls ORDER BY created_at DESC LIMIT 1"
            )
            last_created = cursor.fetchone()
            last_created = last_created[0] if last_created else None

            return {
                "total_urls": total,
                "last_created": last_created
            }