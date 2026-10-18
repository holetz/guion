from sqlalchemy import Column, Integer, String, DATETIME, TIMESTAMP
from sqlalchemy.orm.session import Session
from apps import db

class Permissions(db.Model):
    __tablename__ = 'Permissions'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    id_projeto = Column(String)

    @classmethod
    def has_access(cls, username:str, id_projeto:str):
        permission = db.session.query(cls).filter_by(username=username, id_projeto=id_projeto).first()
        return permission is not None
    
    @classmethod
    def get_accesses(cls, username:str):
        return db.session.query(cls).filter_by(username=username).all()
    
class Carga(db.Model):
    __tablename__ = 'Cargas'

    id_carga = Column(Integer, primary_key=True)
    id_projeto = Column(String)
    dt_carga = Column(TIMESTAMP)
    ds_arquivo = Column(String)
    username = Column(String)
    
class Keychain(db.Model):
    __tablename__ = f'Keychain'
    
    id = Column(Integer, primary_key=True)
    system = Column(String)
    id_projeto = Column(String)
    username = Column(String)
    password = Column(String)
    
    @classmethod
    def get_credentials(cls, system:str, id_projeto:str, session:Session|None = None):
        if session is None:
            session = db.session
            
        credential = session.query(cls).filter_by(system=system, id_projeto=id_projeto).first()
        return {
            'user': credential.username,
            'password': credential.password,
            'system': credential.system,
        }
            
    def set_credentials(cls, system:str, id_projeto:str, user:str, password:str, session:Session|None = None):
        if session is None:
            session = db.session

        session.add(cls(system=system, id_projeto=id_projeto, user=user, password=password))
        session.commit()