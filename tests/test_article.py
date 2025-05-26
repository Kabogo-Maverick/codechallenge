import pytest
from lib.models.article import Article
from lib.models.author import Author
from lib.models.magazine import Magazine
from lib.db.connection import get_connection

@pytest.fixture(autouse=True)
def setup_and_teardown():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles")
    cursor.execute("DELETE FROM authors")
    cursor.execute("DELETE FROM magazines")

    # Insert required magazine for tests
    cursor.execute("INSERT INTO magazines (id, name, category) VALUES (1, 'Test Mag', 'General')")
    conn.commit()
    yield
    cursor.execute("DELETE FROM articles")
    cursor.execute("DELETE FROM authors")
    cursor.execute("DELETE FROM magazines")
    conn.commit()
    conn.close()

def test_article_save_and_find_by_id():
    author = Author("Author One")
    author.save()

    article = Article("My First Article", author.id, 1)
    article.save()

    found = Article.find_by_id(article.id)
    assert found is not None
    assert found.title == "My First Article"
    assert found.author_id == author.id
    assert found.magazine_id == 1

def test_find_by_title():
    author = Author("Author Two")
    author.save()

    article = Article("Unique Title", author.id, 1)
    article.save()

    found = Article.find_by_title("Unique Title")
    assert found is not None
    assert found.id == article.id
    assert found.author_id == author.id

def test_update_article():
    author = Author("Update Author")
    author.save()

    article = Article("Original Title", author.id, 1)
    article.save()

    article.title = "Updated Title"
    article.save()

    updated = Article.find_by_id(article.id)
    assert updated.title == "Updated Title"

def test_author_and_magazine_relationships():
    """Optional: test if article.author() and article.magazine() methods exist."""
    author = Author("Rel Author")
    author.save()

    magazine = Magazine("Rel Mag", "Science")
    magazine.save()

    article = Article("Relational", author.id, magazine.id)
    article.save()

    assert article.author().name == "Rel Author"
    assert article.magazine().name == "Rel Mag"
