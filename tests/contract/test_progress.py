import pytest


def test_progress_returns_list(client):
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    resp = client.get('/progress')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_progress_includes_last_chapter(client):
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    client.post('/book/le-petit-prince/position', json={'chapter_number': 2})
    resp = client.get('/progress')
    data = resp.get_json()
    book_map = {b['book_id']: b for b in data}
    assert book_map['le-petit-prince']['last_chapter'] == 2


def test_progress_null_for_unread_books(client):
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    resp = client.get('/progress')
    data = resp.get_json()
    book_map = {b['book_id']: b for b in data}
    # books without progress should have last_chapter null
    if 'le-petit-prince' in book_map:
        assert book_map['le-petit-prince']['last_chapter'] is None


def test_progress_unauthenticated(client):
    resp = client.get('/progress')
    assert resp.status_code == 302
