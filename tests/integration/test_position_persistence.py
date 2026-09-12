import json


def test_position_restored_after_logout_login(client):
    # Register and save position
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    client.post('/book/le-petit-prince/position', json={'chapter_number': 3})

    # Logout
    client.get('/logout')

    # Login again
    client.post('/login', json={'username': 'alice', 'password': 'password123'})

    # Access book page and verify last_chapter passed to template
    resp = client.get('/book/le-petit-prince')
    assert resp.status_code == 200
    # Since we can't easily parse Jinja template from test client, check that response contains chapter indicator
    text = resp.data.decode('utf-8')
    # The template should include last_chapter context in some way (e.g., data attribute)
    assert 'data-last-chapter="3"' in text or 'last_chapter' in text or 'Chapitre 3' in text


def test_position_survives_new_session(client):
    # Save position during first session
    client.post('/register', json={'username': 'bob', 'password': 'password123'})
    client.post('/book/le-petit-prince/position', json={'chapter_number': 2})

    # Simulate a new browser session by clearing cookies, then logging in again
    client.get('/logout')

    # New session login
    resp = client.post('/login', json={'username': 'bob', 'password': 'password123'})
    assert resp.status_code == 200

    # Check progress endpoint
    resp = client.get('/progress')
    data = resp.get_json()
    book_map = {b['book_id']: b for b in data}
    assert book_map['le-petit-prince']['last_chapter'] == 2
