set -e

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
VENV="$APP_DIR/.venv"

source "$VENV/bin/activate"

cd "$APP_DIR"

exec "$VENV/bin/gunicorn" run:app
