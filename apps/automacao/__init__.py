from flask import Blueprint

blueprint = Blueprint(
    'automacoes_blueprint',
    __name__,
    url_prefix='/automacao'
)
