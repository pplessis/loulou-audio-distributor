import json
import pytest


def test_login_success(client):
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    resp = client.post('/login', json={'username': 'alice', 'password': 'password123'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['message'] == 'Logged in'
    assert 'redirect' in data


def test_login_invalid_password(client):
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    resp = client.post('/login', json={'username': 'alice', 'password': 'wrongpassword'})
    assert resp.status_code == 401
    assert 'Invalid credentials' in resp.get_json()['error']


def test_login_unknown_user(client):
    resp = client.post('/login', json={'username': 'nobody', 'password': 'password123'})
    assert resp.status_code == 401
    assert 'Invalid credentials' in resp.get_json()['error']


def test_login_form_data(client):
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    resp = client.post('/login', data={'username': 'alice', 'password': 'password123'})
    assert resp.status_code == 200


def test_login_missing_fields(client):
    resp = client.post('/login', json={'username': 'alice'})
    assert resp.status_code == 401
