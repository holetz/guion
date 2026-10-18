import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

from . import projeto

def set_logger() -> logging.Logger:
    logger = logging.getLogger("guion")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")


    class OutFilter:
        def filter(self, record):
            return record.levelno == logging.INFO
        
    class ErrFilter:
        def filter(self, record):
            return record.levelno != logging.INFO
        
    if not logger.hasHandlers():
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(
            logging.DEBUG if os.getenv('DEBUG', 'False') == 'True' else logging.INFO
        )
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        out_file_handler = RotatingFileHandler(
            projeto.PROJETO_PATH.joinpath('stdout.log'), mode="a", maxBytes=5 * 1024 * 1024
        )
        out_file_handler.setLevel(logging.DEBUG)
        out_file_handler.addFilter(OutFilter())
        out_file_handler.setFormatter(formatter)
        logger.addHandler(out_file_handler)

        err_file_handler = RotatingFileHandler(
            projeto.PROJETO_PATH.joinpath('stderr.log'), mode="a", maxBytes=5 * 1024 * 1024
        )
        err_file_handler.setLevel(logging.DEBUG)
        err_file_handler.addFilter(ErrFilter())
        err_file_handler.setFormatter(formatter)
        logger.addHandler(err_file_handler)
        
    return logger