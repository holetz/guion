import os

import pytest

# Isolate the suite from a developer's .env: load_dotenv() never overrides variables already set.
os.environ['SECRET_KEY'] = 'test-secret-key'
for name in ('DB_ENGINE', 'DB_NAME', 'DB_USERNAME', 'DB_PASS', 'DB_HOST', 'DB_PORT'):
    os.environ[name] = ''

from apps import create_app, db  # noqa: E402
from apps.config import DebugConfig  # noqa: E402


@pytest.fixture
def app(tmp_path):
    class TestConfig(DebugConfig):
        TESTING = True
        WTF_CSRF_ENABLED = False
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(tmp_path / 'test.sqlite3')

    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.engine.dispose()


@pytest.fixture
def client(app):
    return app.test_client()
