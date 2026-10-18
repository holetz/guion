import pandas as pd
from sqlalchemy import DECIMAL, INTEGER, Column, Date, String

try:
    from .rpa.utils import models
except:
    from rpa.utils import models

class Queue(models.BaseQueue):
    id_pasta = Column(INTEGER)
    nome_reu = Column(String)
    tipo_despesa = Column(String)
    descricao_despesa = Column(String)
    data_despesa = Column(Date)
    nota_despesa = Column(String)
    valor_despesa = Column(DECIMAL)
    arquivos = Column(String)
    
    __template_type__ = '.zip'

    def projeto_transformer(self, df:pd.DataFrame) -> pd.DataFrame:
        return df