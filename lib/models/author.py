from lib.db.connection import get_connection, transaction
from lib.models.article import Article


class Author:
    def __init__(self, name, id=None):
        self.id = id
        self.name = name

    def save(self):
        """Insert or update the author in the database."""
        conn = get_connection()
        cursor = conn.cursor()
        if self.id:
            cursor.execute(
                "UPDATE authors SET name = ? WHERE id = ?", (self.name, self.id)
            )
        else:
            cursor.execute("INSERT INTO authors (name) VALUES (?)", (self.name,))
            self.id = cursor.lastrowid
        conn.commit()
        conn.close()

    @classmethod
    def find_by_id(cls, id):
        """Find an author by ID."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM authors WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        return cls(row["name"], row["id"]) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Find an author by name."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM authors WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()
        return cls(row["name"], row["id"]) if row else None

    def articles(self):
        """Return all Article objects written by this author."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE author_id = ?", (self.id,))
        rows = cursor.fetchall()
        conn.close()
        return [
            Article(row["title"], row["author_id"], row["magazine_id"], id=row["id"])
            for row in rows
        ]

    def magazines(self):
        """Return all Magazine objects this author has written for."""
        from lib.models.magazine import Magazine  # Avoid circular import

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT m.* FROM magazines m
            JOIN articles a ON m.id = a.magazine_id
            WHERE a.author_id = ?
            """,
            (self.id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            Magazine(row["name"], row["category"], id=row["id"]) for row in rows
        ]

    def add_article(self, magazine, title):
        """Create and save a new article for this author in the given magazine."""
        article = Article(title=title, author_id=self.id, magazine_id=magazine.id)
        article.save()
        return article

    def topic_areas(self):
        """Return a list of unique magazine categories this author has written in."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT m.category FROM magazines m
            JOIN articles a ON m.id = a.magazine_id
            WHERE a.author_id = ?
            """,
            (self.id,),
        )
        rows = cursor.fetchall()
        conn.close()
        return [row["category"] for row in rows]

    @classmethod
    def top_author(cls):
        """Return the Author who has written the most articles."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.*, COUNT(ar.id) as article_count FROM authors a
            JOIN articles ar ON a.id = ar.author_id
            GROUP BY a.id
            ORDER BY article_count DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        conn.close()
        return cls(row["name"], row["id"]) if row else None

    @staticmethod
    def add_author_with_articles(author_name, articles_data):
        """
        Insert an author and related articles atomically in a transaction.

        Parameters:
        - author_name (str): Name of the author
        - articles_data (list of dict): Each dict must have 'title' and 'magazine_id'

        Returns:
        - True if success, False if any error
        """
        try:
            with transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO authors (name) VALUES (?) RETURNING id",
                    (author_name,),
                )
                author_id = cursor.fetchone()[0]

                for article in articles_data:
                    cursor.execute(
                        "INSERT INTO articles (title, author_id, magazine_id) VALUES (?, ?, ?)",
                        (article["title"], author_id, article["magazine_id"]),
                    )
            return True
        except Exception as e:
            print(f"Transaction failed: {e}")
            return False
