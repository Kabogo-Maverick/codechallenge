# tests/test_article.py
import pytest
from lib.models.article import Article
from lib.models.author import Author
from lib.db.connection import get_connection

@pytest.fixture(autouse=True)
def setup_and_teardown():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles")
    cursor.execute("DELETE FROM authors")
    conn.commit()
    yield
    conn.close()

def test_article_save_and_find_by_id():
    author = Author("Author One")
    author.save()

    article = Article("My First Article", author.id)
    article.save()

    found = Article.find_by_id(article.id)
    assert found is not None
    assert found.title == "My First Article"
    assert found.author_id == author.id

def test_find_by_title():
    author = Author("Author Two")
    author.save()

    article = Article("Unique Title", author.id)
    article.save()

    found = Article.find_by_title("Unique Title")
    assert found is not None
    assert found.id == article.id
