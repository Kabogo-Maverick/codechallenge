# lib/models/article.py
from lib.db.connection import get_connection

class Article:
    def __init__(self, title, author_id, id=None):
        self.id = id
        self.title = title
        self.author_id = author_id

    def save(self):
        conn = get_connection()
        cursor = conn.cursor()
        if self.id:
            cursor.execute(
                "UPDATE articles SET title = ?, author_id = ? WHERE id = ?",
                (self.title, self.author_id, self.id)
            )
        else:
            cursor.execute(
                "INSERT INTO articles (title, author_id) VALUES (?, ?)",
                (self.title, self.author_id)
            )
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @classmethod
    def find_by_id(cls, id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return cls(row["title"], row["author_id"], row["id"])
        return None

    @classmethod
    def find_by_title(cls, title):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE title = ?", (title,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return cls(row["title"], row["author_id"], row["id"])
        return None
