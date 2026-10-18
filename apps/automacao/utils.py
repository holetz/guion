import zipfile
import io
import json
import multiprocessing
import os
import re
import signal
import subprocess
import sys
from datetime import datetime
from functools import wraps
from importlib import import_module
from io import BytesIO
from multiprocessing import active_children
from pathlib import Path
from typing import Any

import pandas as pd
from flask import abort
from flask_login import current_user
from sqlalchemy import text

from apps import db
from apps.automacao.models import Carga, Permissions

projetos: dict[str, multiprocessing.process] = {}

PYTHONPATH = Path(__file__).resolve().parents[2]
PROJETOS_PATH = PYTHONPATH.joinpath("projetos")


# Projetos Info
def get_projetos_info() -> dict[str, dict[str, str | float]]:
    infos = {}
    for id_projeto in get_projetos_ids():
        info = get_projeto_info(id_projeto)
        info["status"] = get_projeto_status(id_projeto)
        info["progress"] = get_projeto_progress(id_projeto)["progress"]
        infos[id_projeto] = info
    return infos


# Projetos - Utils
def get_projetos_ids(check_access: bool = False) -> list[str]:
    ids_projeto = sorted([path.stem for path in get_projetos_path()])
    if check_access:
        return [
            id_projeto
            for id_projeto, has_access in zip(
                ids_projeto, get_projetos_access(ids_projeto)
            )
            if has_access
        ]
    return ids_projeto


def get_projetos_path() -> list[Path]:
    return [
        path
        for path in [
            get_projeto_path(folder.stem)
            for folder in PROJETOS_PATH.glob("*")
            if folder.is_dir()
        ]
        if not path is None
    ]


def get_projetos_access(ids_projeto: list[str]) -> bool:
    if current_user.policy == "dev":
        return [True for _ in ids_projeto]
    elif current_user.policy == "admin":
        return [id_projeto != "desenvolvimento" for id_projeto in ids_projeto]
    else:
        permissions = [
            permission.id_projeto
            for permission in Permissions.get_accesses(current_user.username)
        ]
        return [id_projeto in permissions for id_projeto in ids_projeto]


# Projeto Info
def get_projeto_info(id_projeto: str) -> dict[str, str]:
    info = get_projeto_json(id_projeto)
    info["status"] = get_projeto_status(id_projeto)
    info["progress"] = get_projeto_progress(id_projeto)
    info["carga"] = get_projeto_carga_info(id_projeto)
    info["template_suffix"] = get_projeto_template(id_projeto).suffix
    return info


def get_projeto_log(id_projeto: str) -> dict[str, str]:
    def read_tail(file_path: Path) -> str:
        file_path.touch()

        with open(file_path, "rb") as file:
            file.seek(0, 2)
            file_size = file.tell()
            max_size = 2 * 1024  # 2Kb
            start_position = max(file_size - max_size, 0)
            file.seek(start_position)
            data = file.read().decode("utf-8", errors="ignore")

        return "\n".join(data[data.find("\n") + 1 :].split("\n")[:-1][::-1])

    projeto_path = get_projeto_path(id_projeto)

    return {
        "stdout": read_tail(projeto_path.joinpath("stdout.log")),
        "stderr": read_tail(projeto_path.joinpath("stderr.log")),
    }


def get_projeto_credenciais(id_projeto: str) -> list[dict[str, str]]:
    sql = text(
        """
        SELECT system, username
        FROM public."Keychain"
        WHERE id_projeto = :id_projeto
    """
    )
    results = db.session.execute(sql, {"id_projeto": id_projeto}).all()
    return [r._asdict() for r in results]

def set_projeto_credencial(id_projeto: str, credencial: dict[str,str]) -> None:
    set_command = "username = :username"
    if credencial['password']:
        set_command += ", password = :password"

    db.session.execute(text(
        f"""
        UPDATE public."Keychain"
        SET {set_command}
        WHERE id_projeto = :id_projeto
        AND system = :system
    """
    ), {**credencial, "id_projeto": id_projeto})
    db.session.commit()


def get_projeto_json(id_projeto: str) -> dict[str, str]:
    return json.loads(get_projeto_path(id_projeto).joinpath("project.json").read_text())


def get_projeto_status(id_projeto: str) -> str:
    projeto = projetos.get(id_projeto)
    if not projeto:
        return "Parado"
    if not projeto.is_alive():
        return "Parado"

    command_text = get_projeto_socket(id_projeto, "command").read_text()
    if command_text == "Pausar":
        return "Pausando"
    if command_text == "Parar":
        return "Parando"

    status_text = get_projeto_socket(id_projeto, "status").read_text()
    if status_text == "":
        return "Desconhecido"
    return status_text


def get_projeto_progress(id_projeto: str) -> dict[str, int | float]:
    sql = text(
        f"""
        SELECT
            results_status,
            count(*) AS count
        FROM public."{id_projeto}" 
        WHERE id_carga = (
            SELECT MAX(id_carga) 
            FROM public."Cargas" 
            WHERE id_projeto = '{id_projeto}'
        )
        GROUP BY results_status
    """
    )
    results = dict(db.session.execute(sql).all())
    results["Total"] = sum(results.values())
    if results["Total"] > 0:
        results["progress"] = (results["Total"] - results.get("Pendente", 0)) / results[
            "Total"
        ]
    else:
        results["progress"] = 0.0
    return results


def get_projeto_carga_info(id_projeto: str) -> dict[str, Any]:
    sql = text(
        f"""
        SELECT *
        FROM public."Cargas" 
        WHERE id_carga = (
            SELECT MAX(id_carga) 
            FROM public."Cargas" 
            WHERE id_projeto = '{id_projeto}'
        )
    """
    )
    results = db.session.execute(sql).all()
    if not results:
        return {}
    results = results[0]._asdict()
    results["dt_carga"] = results["dt_carga"].strftime("%d/%m/%y %H:%M")
    return results


def get_projeto_template(id_projeto: str):
    return list(get_projeto_path(id_projeto).glob("template.*"))[0]


# Projeto Command
def set_projeto_command(id_projeto: str, command: str):
    if command == "start":
        if get_projeto_status(id_projeto) == "Pausado":
            get_projeto_socket(id_projeto, "command").write_text("Continuar")
            return "Projeto reiniciado com sucesso"
        else:
            if id_projeto in projetos:
                if projetos[id_projeto].is_alive():
                    return "Projeto já em execução"
                else:
                    projetos.pop(id_projeto)
                    
            def signal_handler(sig, frame):
                active = active_children()
                for child in active:
                    child.terminate()
                sys.exit(0)

            def run_subprocess(path) -> None:
                signal.signal(signal.SIGTERM, signal_handler)
                subprocess.run(
                    ["python", path],
                    **(
                        dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if (os.getenv('DEBUG', 'False') == 'True') else
                        {}
                    )
                )

            projetos[id_projeto] = multiprocessing.Process(
                target=run_subprocess,
                args=(str(get_projeto_path(id_projeto).joinpath("main.py")),),
            )
            projetos[id_projeto].start()
            get_projeto_socket(id_projeto, "status").write_text("Iniciando")
            return "Projeto iniciado com sucesso"
    if command == "pause":
        get_projeto_socket(id_projeto, "command").write_text("Pausar")
        return "Projeto pausado com sucesso"
    if command == "stop":
        get_projeto_socket(id_projeto, "command").write_text("Parar")
        return "Projeto encerrado com sucesso"
    else:
        raise AssertionError("Comando não reconhecido")


# Projeto Access
def has_projeto_access(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if "id_projeto" in kwargs:
            if not get_projeto_access(kwargs["id_projeto"]):
                abort(403)
        return func(*args, **kwargs)

    return decorated_view


def get_projeto_access(id_projeto: str) -> bool:
    return (
        current_user.policy == "dev"
        or (current_user.policy == "admin" and id_projeto != "desenvolvimento")
        or Permissions.has_access(current_user.username, id_projeto)
    )


# Projeto Carga
def get_projeto_carga(id_projeto: str, status: str) -> dict[str, dict[str, Any]]:
    status = status.capitalize()
    status = {"Concluido": "Concluído"}.get(status, status)
    assert status in (
        "Pendente",
        "Concluído",
        "Erro",
    ), f"Status não reconhecido: {status}"

    columns = {
        row.column_name:row.data_type
        for row in db.session.execute(
            text(
                f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = '{id_projeto}';
        """
            )
        ).all()
        if not row.column_name in ("id", "id_carga", "results_status", "results_json", "results_stacktrace", "download_bytes")
        and (row.column_name != "results_error" or status == 'Erro')
    }
    columns_name = [{'results_error':'Erro'}.get(k,k) for k in columns.keys()]

    results = db.session.execute(
        text(
            f"""
        SELECT 
            {','.join([
                f"TO_CHAR({column_name}, 'DD/MM/YYYY') AS {column_name}"
                if data_type == 'date' else
                'results_error AS "Erro"'
                if column_name == 'results_error'
                else
                column_name
                for column_name, data_type in columns.items()
            ])}
        FROM public."{id_projeto}" 
        WHERE id_carga = (
            SELECT MAX(id_carga) 
            FROM public."Cargas" 
            WHERE id_projeto = '{id_projeto}'
        )
        AND results_status = '{status}'
    """
        )
    ).all()

    return dict(columns=columns_name, rows=[r._asdict() for r in results])


def get_projeto_cargas(id_projeto: str) -> list[dict[str,Any]]:
    results = db.session.execute(
        text(
            f"""
                SELECT 
                    t1.id_carga,
                    TO_CHAR(dt_carga, 'DD/MM/YYYY HH24:MI:SS') AS dt_carga,
                    ds_arquivo,
                    username,
                    coalesce(count_total,0) AS count_total,
                    coalesce(count_pendente,0) AS count_pendente,
                    coalesce(count_concluido,0) AS count_concluido,
                    coalesce(count_erro,0) AS count_erro
                FROM
                    public."Cargas" AS t1
                    LEFT JOIN (
                        SELECT
                            id_carga,
                            count(*) AS count_total,
                            count(*) FILTER (WHERE results_status = 'Pendente') AS count_pendente,
                            count(*) FILTER (WHERE results_status = 'Concluído') AS count_concluido,
                            count(*) FILTER (WHERE results_status = 'Erro') AS count_erro
                        FROM public."{id_projeto}"
                        GROUP BY id_carga
                    ) AS t2 ON t1.id_carga = t2.id_carga
                WHERE id_projeto = '{id_projeto}'
            """
        )
    ).all()

    return [r._asdict() for r in results]


def set_projeto_carga(id_projeto: str, file: io.BytesIO, file_name:str):
    carga = Carga(
        id_projeto = id_projeto,
        dt_carga = datetime.now(),
        ds_arquivo = file_name,
        username = current_user.username,
    )
    db.session.add(carga)
    db.session.commit()

    module = import_module(f"projetos.{id_projeto}.model")
    module.Queue().set_queue(id_carga=carga.id_carga, file=file)

def clear_projeto_carga_erros(id_projeto: str):
    db.session.execute(
        text(
            f"""
                UPDATE public."{id_projeto}" 
                SET results_status = 'Pendente', results_error = null, results_stacktrace = null, results_json = null
                WHERE id_carga = (
                    SELECT MAX(id_carga) 
                    FROM public."Cargas" 
                    WHERE id_projeto = '{id_projeto}' and not results_error like 'CRÍTICO - %'
                )
                AND results_status = 'Erro'
            """
        )
    )
    db.session.commit()

def get_projeto_carga_relatorio(id_projeto: str, id_carga: str):
    # carregar dados
    data = pd.DataFrame([
        row._asdict()
        for row in db.session.execute(
            text(f'''SELECT * FROM public."{id_projeto}" WHERE id_carga = {id_carga}''')
        ).all()
    ])

    # limpar stacktrace se não for dev
    if current_user.policy != "dev":
        if "results_stacktrace" in data.columns:
            data.drop(columns=["results_stacktrace"], inplace=True)

    has_binary = (
        "download" in data.columns
        and "download_bytes" in data.columns
    )

    # ---------- CASO ZIP ----------
    if has_binary:
        # Excel sem bytes
        excel_buffer = BytesIO()
        data_excel = data.drop(columns=["download_bytes"], errors="ignore")
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            data_excel.to_excel(writer, index=False, sheet_name="Relatório")
        excel_buffer.seek(0)

        # Criar zip
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:

            # adicionar arquivos binários
            for _, row in data.iterrows():
                filename = row["download"]
                content = row["download_bytes"]

                if isinstance(content, memoryview):
                    content = content.tobytes()
                    
                if filename and isinstance(content, (bytes, bytearray)):
                    zf.writestr(filename, content)

            # adicionar excel ao zip
            zf.writestr("relatorio.xlsx", excel_buffer.read())

        zip_buffer.seek(0)
        return ("zip", zip_buffer)

    # ---------- CASO EXCEL NORMAL ----------
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        data.to_excel(writer, index=False, sheet_name="Relatório")
    output.seek(0)

    return ("excel", output)

# Projeto Input
def get_projeto_input(id_projeto) -> dict[str, Any] | None:
    try:
        with open(get_projeto_socket(id_projeto, "input"), "r") as f:
            params = json.load(f)
        return params
    except:
        return None


def set_projeto_response(id_projeto, data) -> dict[str, Any] | None:
    input_path = get_projeto_socket(id_projeto, "input")
    response_path = get_projeto_socket(id_projeto, "response")
    with open(response_path, "w") as f:
        json.dump(data, f)
    input_path.write_text("")
    
    
# Projeto - Utils
def get_projeto_path(id_projeto: str) -> Path | None:
    projeto_path = PROJETOS_PATH.joinpath(id_projeto).absolute()
    projeto_json = projeto_path.joinpath('project.json')
    
    if projeto_json.exists():
        project_dict = json.loads(projeto_json.read_text())
        if project_dict.get('enabled',False):
            return projeto_path


def get_projeto_socket(id_projeto: str, socket_name: str) -> Path:
    assert socket_name in [
        "command",
        "status",
        "input",
        "response",
    ], "socket_name not recognized"
    socket_path = get_projeto_path(id_projeto).joinpath(f"socket_{socket_name}")
    socket_path.touch()
    return socket_path


def get_projeto_static(id_projeto, filename: str) -> io.BytesIO:
    input_path = get_projeto_path(id_projeto).joinpath("static", filename)
    if input_path.exists():
        return io.BytesIO(input_path.read_bytes())
    return io.BytesIO()
