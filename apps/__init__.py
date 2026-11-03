import logging
import os
from pathlib import Path

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from sqlalchemy import create_engine


db = SQLAlchemy()
login_manager = LoginManager()
logger = logging.getLogger(__name__)


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home', 'automacao'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)

def register_projetos():
    for f in Path('projetos').glob('*/model.py'):
        model_path = str(f).replace('/','.').replace('\\','.').replace('.py','')
        import_module(model_path).Queue.__table__.metadata = db.metadata

def refresh_database(app):
    register_projetos()
    db.create_all()


def select_database(app):
    """Fall back to SQLite when the configured DBMS cannot be reached.

    Runs before the extension binds its engine, so the fallback URI is the one used.
    """
    uri = app.config['SQLALCHEMY_DATABASE_URI']
    if uri.startswith('sqlite'):
        return
    try:
        engine = create_engine(uri)
        with engine.connect():
            pass
        engine.dispose()
    except Exception as e:
        logger.error('DBMS exception: %s', e)
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
        logger.warning('Falling back to SQLite')


def configure_database(app):
    register_projetos()
    with app.app_context():
        db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    select_database(app)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    return app
