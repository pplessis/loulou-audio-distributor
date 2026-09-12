import os
import json


def test_full_auth_flow(client):
    # Register
    resp = client.post('/register', json={'username': 'dave', 'password': 'password123'})
    assert resp.status_code == 201

    # Access protected route
    resp = client.get('/')
    assert resp.status_code == 200

    # Logout
    resp = client.get('/logout')
    assert resp.status_code == 302  # redirect

    # Access protected route after logout should redirect to login
    resp = client.get('/book/le-petit-prince')
    assert resp.status_code == 302

    # Login again
    resp = client.post('/login', json={'username': 'dave', 'password': 'password123'})
    assert resp.status_code == 200

    # Access protected route after re-login
    resp = client.get('/book/le-petit-prince')
    assert resp.status_code == 200


def test_registration_creates_user_file(client):
    client.post('/register', json={'username': 'eve', 'password': 'password123'})
    from app.services.auth_service import USERS_FILE
    assert os.path.exists(USERS_FILE)
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        users = json.load(f)
    usernames = [u['username'] for u in users.values()]
    assert 'eve' in usernames
