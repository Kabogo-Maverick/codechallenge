import pytest
from lib.models.author import Author
from lib.models.magazine import Magazine
from lib.models.article import Article
from lib.db.connection import get_connection

@pytest.fixture
def setup_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles")
    cursor.execute("DELETE FROM authors")
    cursor.execute("DELETE FROM magazines")

    # Insert required magazines for foreign key references
    cursor.execute("INSERT INTO magazines (id, name, category) VALUES (1, 'Tech Mag', 'Tech'), (2, 'Science Mag', 'Science')")
    conn.commit()
    yield
    cursor.execute("DELETE FROM articles")
    cursor.execute("DELETE FROM authors")
    cursor.execute("DELETE FROM magazines")
    conn.commit()
    conn.close()

def test_add_author_with_articles(setup_db):
    articles_data = [
        {'title': 'Transactional Article 1', 'magazine_id': 1},
        {'title': 'Transactional Article 2', 'magazine_id': 2}
    ]
    result = Author.add_author_with_articles("Transactional Author", articles_data)
    assert result is True

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM authors WHERE name = ?", ("Transactional Author",))
    author = cursor.fetchone()
    assert author is not None

    cursor.execute("SELECT * FROM articles WHERE author_id = ?", (author["id"],))
    articles = cursor.fetchall()
    assert len(articles) == 2
    titles = [article["title"] for article in articles]
    assert "Transactional Article 1" in titles
    assert "Transactional Article 2" in titles
    conn.close()

def test_create_and_find_author(setup_db):
    author = Author("Test Author")
    author.save()
    found = Author.find_by_id(author.id)
    assert found is not None
    assert found.name == "Test Author"

def test_find_by_name(setup_db):
    author = Author("Unique Author")
    author.save()
    found = Author.find_by_name("Unique Author")
    assert found is not None
    assert found.id == author.id

def test_add_article_and_articles_method(setup_db):
    author = Author("Writer")
    author.save()
    magazine = Magazine("Weekly News", "News")
    magazine.save()
    article = author.add_article(magazine, "Breaking News")
    assert article.title == "Breaking News"
    articles = author.articles()
    assert any(a.title == "Breaking News" for a in articles)

def test_magazines_and_topic_areas(setup_db):
    author = Author("Contributor")
    author.save()
    mag1 = Magazine("Tech Journal", "Tech")
    mag2 = Magazine("Health Digest", "Health")
    mag1.save()
    mag2.save()
    author.add_article(mag1, "Tech Trends")
    author.add_article(mag2, "Wellness Guide")

    magazines = author.magazines()
    assert len(magazines) == 2
    topics = author.topic_areas()
    assert "Tech" in topics
    assert "Health" in topics

def test_top_author(setup_db):
    author = Author("Prolific Writer")
    author.save()
    magazine = Magazine("Top Mag", "Popular")
    magazine.save()
    Article("Top Article 1", author.id, magazine.id).save()
    Article("Top Article 2", author.id, magazine.id).save()
    Article("Top Article 3", author.id, magazine.id).save()

    top = Author.top_author()
    assert top.name == "Prolific Writer"
