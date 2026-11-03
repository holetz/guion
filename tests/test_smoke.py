import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_app_boots(app):
    assert app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite')


def test_login_page_renders(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b'name="login"' in response.data


def test_register_page_renders(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b'name="register"' in response.data


def test_register_then_login(client):
    response = client.post('/register', data={
        'username': 'alice', 'email': 'alice@example.com',
        'password': 'correct horse', 'register': '',
    })
    assert response.status_code == 302
    assert '/login' in response.location

    response = client.post('/login', data={
        'username': 'alice', 'password': 'correct horse', 'login': '',
    })
    assert response.status_code == 302

    response = client.get('/index')
    assert response.status_code == 302
    assert response.location.endswith('/automacao/projetos')


def test_wrong_password_is_rejected(client):
    client.post('/register', data={
        'username': 'bob', 'email': 'bob@example.com', 'password': 'right', 'register': '',
    })
    response = client.post('/login', data={'username': 'bob', 'password': 'wrong', 'login': ''})
    assert response.status_code == 200
    assert 'Usuário ou senha errado'.encode() in response.data


def test_protected_page_refuses_anonymous(client):
    response = client.get('/index')
    assert response.status_code == 403


def test_production_without_secret_key_exits():
    env = {**os.environ, 'DEBUG': 'False', 'SECRET_KEY': ''}
    result = subprocess.run([sys.executable, '-c', 'import run'], cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=120)
    assert result.returncode != 0
    assert 'SECRET_KEY is not set' in result.stderr
