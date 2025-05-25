# tests/test_magazine.py

import pytest
from lib.models.magazine import Magazine
from lib.db.connection import get_connection

@pytest.fixture(autouse=True)
def setup_and_teardown():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM magazines")
    conn.commit()
    conn.close()
    yield

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
