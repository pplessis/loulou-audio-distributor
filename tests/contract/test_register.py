import json
import os
import pytest


def test_register_success(client):
    resp = client.post('/register', json={'username': 'alice', 'password': 'password123'})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['message'] == 'Account created'
    assert 'redirect' in data


def test_register_missing_fields(client):
    resp = client.post('/register', json={'username': 'alice'})
    assert resp.status_code == 400
    assert 'error' in resp.get_json()


def test_register_password_too_short(client):
    resp = client.post('/register', json={'username': 'alice', 'password': 'short'})
    assert resp.status_code == 400
    assert 'at least 8 characters' in resp.get_json()['error']


def test_register_duplicate_username(client):
    client.post('/register', json={'username': 'alice', 'password': 'password123'})
    resp = client.post('/register', json={'username': 'alice', 'password': 'password456'})
    assert resp.status_code == 409
    assert 'already exists' in resp.get_json()['error']


def test_register_form_data(client):
    resp = client.post('/register', data={'username': 'bob', 'password': 'password123'})
    assert resp.status_code == 201


def test_register_trim_username(client):
    resp = client.post('/register', json={'username': '  charlie  ', 'password': 'password123'})
    assert resp.status_code == 201
    # Ensure whitespace is stripped (duplicate check should use trimmed username)
    resp2 = client.post('/register', json={'username': 'charlie', 'password': 'password456'})
    assert resp2.status_code == 409
