# tests/test_author.py
import os
import sqlite3
import pytest
from lib.models.author import Author
from lib.db.connection import get_connection

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Reset DB before each test
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles")
    cursor.execute("DELETE FROM authors")
    conn.commit()
    yield
    conn.close()

def test_author_save_and_find_by_id():
    author = Author("Jane Doe")
    author.save()

    found = Author.find_by_id(author.id)
    assert found is not None
    assert found.name == "Jane Doe"

def test_find_by_name():
    author = Author("John Smith")
    author.save()

    found = Author.find_by_name("John Smith")
    assert found is not None
    assert found.id == author.id
