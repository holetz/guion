import logging
import os
from flask_migrate import Migrate
from flask_minify import Minify
from sqlalchemy.engine import make_url
from sys import exit

from apps.config import config_dict
from apps import create_app, db
from dotenv import load_dotenv
load_dotenv()  # loads .env from project root by default

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger(__name__)

# WARNING: Don't run with debug turned on in production!

DEBUG = os.getenv('DEBUG', 'False') == 'True'

# The configuration
get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

try:
    app_config.validate()
except RuntimeError as e:
    exit('Error: {}'.format(e))

app = create_app(app_config)
Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if DEBUG:
    logger.info('DEBUG            = %s', DEBUG)
    logger.info('Page Compression = %s', 'FALSE' if DEBUG else 'TRUE')
    logger.info('DBMS             = %s',
                make_url(app.config['SQLALCHEMY_DATABASE_URI']).render_as_string(hide_password=True))
    logger.info('ASSETS_ROOT      = %s', app_config.ASSETS_ROOT)

if __name__ == "__main__":
    app.run()
