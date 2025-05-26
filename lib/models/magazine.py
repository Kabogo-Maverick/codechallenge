# lib/models/magazine.py

from lib.db.connection import get_connection, transaction
from lib.models.article import Article

class Magazine:
    def __init__(self, name, category, id=None):
        self.id = id
        self.name = name
        self.category = category

    def save(self):
        """Insert or update a magazine record in the database."""
        conn = get_connection()
        cursor = conn.cursor()
        if self.id:
            cursor.execute(
                "UPDATE magazines SET name = ?, category = ? WHERE id = ?",
                (self.name, self.category, self.id)
            )
        else:
            cursor.execute(
                "INSERT INTO magazines (name, category) VALUES (?, ?)",
                (self.name, self.category)
            )
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @classmethod
    def find_by_id(cls, id):
        """Find a magazine by its ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM magazines WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        return cls(row["name"], row["category"], row["id"]) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Find a magazine by its name."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM magazines WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        return cls(row["name"], row["category"], row["id"]) if row else None

    def articles(self):
        """Return all articles published in this magazine."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE magazine_id = ?", (self.id,))
        rows = cursor.fetchall()
        conn.close()
        return [Article(row["title"], row["author_id"], row["magazine_id"], id=row["id"]) for row in rows]

    def contributors(self):
        """Return distinct authors who have written for this magazine."""
        from lib.models.author import Author
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT a.* FROM authors a
            JOIN articles ar ON a.id = ar.author_id
            WHERE ar.magazine_id = ?
        """, (self.id,))
        rows = cursor.fetchall()
        conn.close()
        return [Author(row["name"], row["id"]) for row in rows]

    def authors(self):
        """Return raw rows of authors who wrote for this magazine (internal use)."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT a.* FROM authors a
            JOIN articles ar ON a.id = ar.author_id
            WHERE ar.magazine_id = ?
        """, (self.id,))
        return cursor.fetchall()

    @classmethod
    def magazines_with_multiple_authors(cls):
        """
        Return magazines that have articles written by more than one unique author.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.* FROM magazines m
            JOIN articles a ON m.id = a.magazine_id
            GROUP BY m.id
            HAVING COUNT(DISTINCT a.author_id) > 1
        """)
        return cursor.fetchall()

    @classmethod
    def article_counts(cls):
        """
        Return a list of magazines and the number of articles they contain.
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, m.name, COUNT(a.id) as article_count
            FROM magazines m
            LEFT JOIN articles a ON m.id = a.magazine_id
            GROUP BY m.id
        """)
        return cursor.fetchall()

    @staticmethod
    def add_magazine_with_articles(name, category, articles_data):
        """
        Adds a new magazine along with its associated articles in a single transaction.

        Args:
            name (str): Name of the magazine.
            category (str): Category of the magazine.
            articles_data (list[dict]): Each dict contains 'title' and 'author_id'.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO magazines (name, category) VALUES (?, ?) RETURNING id",
                    (name, category)
                )
                magazine_id = cursor.fetchone()[0]

                for article in articles_data:
                    cursor.execute(
                        "INSERT INTO articles (title, author_id, magazine_id) VALUES (?, ?, ?)",
                        (article['title'], article['author_id'], magazine_id)
                    )
            return True
        except Exception as e:
            print(f"Transaction failed: {e}")
            return False
