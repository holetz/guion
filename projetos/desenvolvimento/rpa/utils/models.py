import io
import shutil
import zipfile
from functools import cached_property

import pandas as pd
from sqlalchemy import INTEGER, Column, Index, String
from sqlalchemy.dialects.postgresql import JSON

from . import projeto

from apps import db

class BaseQueue(db.Model):
    id = Column(INTEGER, primary_key=True)
    id_carga = Column(INTEGER)
    results_status = Column(String, default='Pendente')
    results_error = Column(String)
    results_stacktrace = Column(String)
    results_json = Column(JSON)

    __tablename__ = projeto.ID_PROJETO
    __table_args__ = (Index(None, 'id_carga', 'results_status'),)
    __template_type__ = ''

    @cached_property
    def columns(self) -> list[str]:
        return [c.name for c in self.__table__.columns]
    
    @cached_property
    def process_columns(self) -> list[str]:
        return [c for c in self.columns if not c in ['id','id_carga','results_status','results_error','results_json','results_stacktrace']]
    
    def __repr__(self) -> str:
        return '; '.join([f'{col}:{getattr(self,col)}' for col in self.process_columns])
    
    def projeto_transformer(self, df:pd.DataFrame) -> pd.DataFrame:
        raise NotImplemented('Função não implementada')
    
    def set_queue(self, id_carga:int, file:io.BytesIO):    
        if self.__template_type__ == ".zip":
            # Para cargas zipadas com o layout de arquivos
            with zipfile.ZipFile(file, "r") as zip_file:
                xlsx_files = [
                    file
                    for file in zip_file.namelist()
                    if not "/" in file and file.endswith("xlsx")
                ]
                
                assert len(xlsx_files) > 0, 'Nenhuma planilha de carga ".xslx" encontrada na raiz do arquivo informado'
                assert len(xlsx_files) == 1, 'Mais de uma planilha de carga ".xlsx" encontrada na raiz do arquivo informado'
                
                carga_xlsx = io.BytesIO(zip_file.read(xlsx_files[0]))
                carga_anexos = [
                    file for file in zip_file.namelist()
                    if file.startswith("arquivos/") and not file.endswith("/")
                ]

                carga_pdf = pd.read_excel(carga_xlsx)
                carga_pdf.columns = [c.lower() for c in carga_pdf.columns]
                assert 'arquivos' in carga_pdf.columns, 'Nenhum campo "arquivos" na carga informada'
                
                missing_carga_anexos = [
                    file for file in pd.read_excel(carga_xlsx)["arquivos"].fillna("").to_list()
                    if not file == "" and not f"arquivos/{file}" in carga_anexos
                ]

                assert len(missing_carga_anexos) == 0, f"Arquivos listados não encontrados. Ex: {missing_carga_anexos[0]}"

                try:
                    shutil.rmtree(projeto.PROJETO_PATH.joinpath("arquivos"))
                except:
                    pass

                for attachment in carga_anexos:
                    zip_file.extract(attachment, path=projeto.PROJETO_PATH)

        elif self.__template_type__ == ".xlsx":
            carga_xlsx = file
        else:
            raise AssertionError(f"Formato da carga não reconhecido: {self.__template_type__}")

        df = pd.read_excel(carga_xlsx,dtype=str).fillna('')
        assert df.columns.to_list() == self.process_columns, 'As colunas do arquivo não correspondem ao layout de carga'
        db.session.bulk_insert_mappings(
            self, 
            (
                self.projeto_transformer(df)
                .replace([float('nan')], [None], regex=False)
                .assign(id_carga=id_carga)
                .to_dict(orient='records')
            )
        )
        db.session.commit()