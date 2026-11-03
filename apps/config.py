# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import logging
import os
import secrets

from dotenv import load_dotenv
load_dotenv()  # loads .env from project root by default

logger = logging.getLogger(__name__)

class Config(object):

    basedir = os.path.abspath(os.path.dirname(__file__))

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

    # Set up the App SECRET_KEY; checked by validate() before the app starts
    SECRET_KEY  = os.getenv('SECRET_KEY') or None

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_ENGINE   = os.getenv('DB_ENGINE'   , None)
    DB_USERNAME = os.getenv('DB_USERNAME' , None)
    DB_PASS     = os.getenv('DB_PASS'     , None)
    DB_HOST     = os.getenv('DB_HOST'     , None)
    DB_PORT     = os.getenv('DB_PORT'     , None)
    DB_NAME     = os.getenv('DB_NAME'     , None)

    USE_SQLITE  = True 

    print(DB_ENGINE, DB_NAME, DB_USERNAME)
    # try to set up a Relational DBMS
    if DB_ENGINE and DB_NAME and DB_USERNAME:

        try:
            
            # Relational DBMS: PSQL, MySql
            SQLALCHEMY_DATABASE_URI = '{}://{}:{}@{}:{}/{}'.format(
                DB_ENGINE,
                DB_USERNAME,
                DB_PASS,
                DB_HOST,
                DB_PORT,
                DB_NAME
            ) 

            USE_SQLITE  = False

        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )
            print('> Fallback to SQLite ')    

    if USE_SQLITE:

        # This will create a file in <app> FOLDER
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3') 
    
    @classmethod
    def validate(cls):
        """Check the configuration before the app starts."""


class ProductionConfig(Config):
    DEBUG = False

    @classmethod
    def validate(cls):
        if not cls.SECRET_KEY:
            raise RuntimeError(
                'SECRET_KEY is not set. Production needs a fixed secret key: set SECRET_KEY '
                'in .env (see .env.example), e.g. with '
                '`python -c "import secrets; print(secrets.token_hex(32))"`.'
            )

    # Security
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600


class DebugConfig(Config):
    DEBUG = True

    @classmethod
    def validate(cls):
        if not cls.SECRET_KEY:
            cls.SECRET_KEY = secrets.token_hex(32)
            logger.warning('SECRET_KEY is not set; using a random key for this process '
                           '(sessions end on restart). Set SECRET_KEY in .env.')


# Load all possible configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug'     : DebugConfig
}
