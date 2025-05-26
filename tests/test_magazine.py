import pytest
from lib.models.magazine import Magazine
from lib.models.author import Author
from lib.models.article import Article
from lib.db.connection import get_connection

@pytest.fixture(autouse=True)
def setup_and_teardown():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles")
    cursor.execute("DELETE FROM authors")
    cursor.execute("DELETE FROM magazines")
    conn.commit()
    conn.close()
    yield
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles")
    cursor.execute("DELETE FROM authors")
    cursor.execute("DELETE FROM magazines")
    conn.commit()
    conn.close()

def test_magazine_save_and_find_by_id():
    mag = Magazine("Tech Monthly", "Technology")
    mag.save()

    found = Magazine.find_by_id(mag.id)
    assert found is not None
    assert found.name == "Tech Monthly"
    assert found.category == "Technology"

def test_find_by_name():
    mag = Magazine("Science Weekly", "Science")
    mag.save()

    found = Magazine.find_by_name("Science Weekly")
    assert found is not None
    assert found.id == mag.id
    assert found.category == "Science"

def test_magazines_with_multiple_authors():
    mag = Magazine("Multi Author Mag", "Various")
    mag.save()

    author1 = Author("Author One")
    author1.save()
    author2 = Author("Author Two")
    author2.save()

    Article("Article 1", author1.id, mag.id).save()
    Article("Article 2", author2.id, mag.id).save()

    results = Magazine.magazines_with_multiple_authors()
    ids = [row["id"] for row in results]
    assert mag.id in ids

def test_article_counts():
    mag1 = Magazine("Article Count Mag", "News")
    mag2 = Magazine("Empty Mag", "None")
    mag1.save()
    mag2.save()

    author = Author("Counting Author")
    author.save()

    Article("A1", author.id, mag1.id).save()
    Article("A2", author.id, mag1.id).save()

    results = Magazine.article_counts()
    counts = {row["name"]: row["article_count"] for row in results}

    assert counts["Article Count Mag"] == 2
    assert counts["Empty Mag"] == 0
