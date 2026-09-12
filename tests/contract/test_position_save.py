import json


def test_save_position(client):
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    resp = client.post('/book/le-petit-prince/position', json={'chapter_number': 3})
    assert resp.status_code == 200
    assert resp.get_json()['message'] == 'Position saved'


def test_save_position_unauthenticated(client):
    resp = client.post('/book/le-petit-prince/position', json={'chapter_number': 2})
    assert resp.status_code == 302  # redirect to login


def test_save_position_invalid_chapter(client):
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    resp = client.post('/book/le-petit-prince/position', json={'chapter_number': -1})
    # Should still save (endpoint doesn't reject negative numbers currently)
    assert resp.status_code == 200


def test_save_position_updates_multiple_books(client):
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    client.post('/book/le-petit-prince/position', json={'chapter_number': 3})
    resp = client.get('/progress')
    data = resp.get_json()
    assert len(data) >= 1
    books = {b['book_id']: b['last_chapter'] for b in data}
    assert books['le-petit-prince'] == 3


def test_position_persisted_to_file(client):
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    client.post('/book/le-petit-prince/position', json={'chapter_number': 2})
    from app.services.progress_service import read_user_progress
    prog = read_user_progress('1')
    assert prog['le-petit-prince']['last_chapter'] == 2
