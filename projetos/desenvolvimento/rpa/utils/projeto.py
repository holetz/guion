import re
import sys
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

PYTHONPATH = str(Path(__file__).resolve().parents[4])

if not PYTHONPATH in sys.path:
    sys.path.append(PYTHONPATH)

from apps import config

PROJETOS_PATH = Path(f'{PYTHONPATH}/projetos')
DATABASE_URL = config.Config.SQLALCHEMY_DATABASE_URI
DATABASE_ENGINE:Engine = create_engine(DATABASE_URL)
ID_PROJETO = re.findall('.*?/projetos/(.*?)/.*',__file__)[0]
PROJETO_PATH = PROJETOS_PATH.joinpath(ID_PROJETO)

if not PROJETO_PATH in sys.path:
    sys.path.append(PROJETO_PATH)

def get_template_suffix() -> str:
    return list(PROJETO_PATH.glob('template.*'))[0].suffix

def get_db_session() -> Session:
    return sessionmaker(DATABASE_ENGINE)()