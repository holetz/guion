import json
import logging
import time
from io import BytesIO
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm.session import Session

from . import projeto
from . import logger

class Controller:
    session: Session
    command_file: Path
    status_file: Path
    input_file: Path
    response_file: Path
    projeto_path: Path
    id_projeto: str
    
    logger: logging.Logger
    model: object

    def __init__(self, model: object):
        self.session = projeto.get_db_session()

        self.projeto_path = projeto.PROJETO_PATH
        self.id_projeto = projeto.ID_PROJETO
        
        self.command_file = self.projeto_path.joinpath("socket_command")
        self.status_file = self.projeto_path.joinpath("socket_status")
        self.input_file = self.projeto_path.joinpath("socket_input")
        self.response_file = self.projeto_path.joinpath("socket_response")
        
        self.command_file.touch()
        self.status_file.touch()
        self.input_file.touch()
        self.response_file.touch()
        
        self.logger = logger.set_logger()
        self.model = model

    def yield_command(self):
        while True:
            time.sleep(0.5)
            if self.command_file.read_text() == "Pausar":
                self.status_file.write_text("Pausado")
                self.command_file.write_text("")
                time.sleep(1)

            elif self.command_file.read_text() == "Parar":
                self.status_file.write_text("")
                self.command_file.write_text("")
                raise KeyboardInterrupt()

            elif self.command_file.read_text() == "Continuar":
                self.status_file.write_text("Executando")
                self.command_file.write_text("")
                break

            elif self.status_file.read_text() == "Pausado":
                pass

            else:
                break

        self.status_file.write_text("Executando")

    def clear_status(self):
        self.command_file.write_text("")
        self.input_file.write_text("")
        self.response_file.write_text("")

    def get_next_queue(self, where:str='') -> tuple[object | None, list[Path]]:
        id_carga = self.session.execute(text(
            f"""
                SELECT MAX(id_carga) AS id_carga
                FROM public."Cargas" 
                WHERE id_projeto = '{self.id_projeto}'
            """
        )).first().id_carga

        next_queue = (
            self.session.query(self.model)
            .where(text(f"id_carga = '{id_carga}'"))
            .where(text(where or "results_status = 'Pendente'"))
            .first()
        )

        files = []
        if not next_queue is None:
            if hasattr(next_queue, "arquivos") and str(next_queue.arquivos):
                for pattern in str(next_queue.arquivos).split("|"):
                    files.extend(self.projeto_path.joinpath("arquivos").glob(pattern))
        return next_queue, files
    
    def get_input(
        self,
        title: str,
        question: str,
        image: BytesIO | None = None,
        options: list[str] | None = None,
    ) -> str:
        print(1)
        json_input:dict[str,Any] = dict(title=title, question=question)
        if image is not None:
            image_path = self.projeto_path.joinpath("static", image.name)
            image_path.touch()
            image_path.write_bytes(image.getbuffer())
            json_input['image'] = image.name
        if options is not None:
            json_input['options'] = list(map(str,options))
        
        try:
            dev = __IPYTHON__
        except:
            dev = False
            
        if dev:
            return input()
        else:
            self.response_file.write_text('')
            with open(self.input_file,'w') as f:
                json.dump(json_input, f)

            status_memory = self.status_file.read_text()
            self.status_file.write_text("Input")
            while len(self.input_file.read_text()) > 0:
                time.sleep(1)
            self.status_file.write_text(status_memory)

            with open(self.response_file,'r') as f:
                return json.load(f)