from apps.automacao import blueprint
from apps.automacao import utils
from flask import jsonify, render_template, redirect, send_file, request, current_app
from flask_login import login_required
from apps import refresh_database

import io
from datetime import timedelta, timezone, datetime


@blueprint.route("/")
@login_required
def default():
    return redirect("projetos")


@blueprint.route("/projetos")
@login_required
def projetos():
    refresh_database(current_app)
    return render_template(
        "automacao/projetos.html", ids_projeto=utils.get_projetos_ids(check_access=True)
    )


@blueprint.route("/projetos/get_info", methods=["GET"])
@login_required
def get_projetos_info():
    return jsonify(utils.get_projetos_info()), 200


@blueprint.route("/projeto/<id_projeto>/")
@login_required
@utils.has_projeto_access
def projeto(id_projeto: str):
    return render_template("automacao/projeto.html", id_projeto=id_projeto, nome_projeto=utils.get_projeto_json(id_projeto).get('name','Projeto'))


@blueprint.route("/projeto/<id_projeto>/get_info", methods=["GET"])
@login_required
@utils.has_projeto_access
def get_projeto_info(id_projeto: str):
    return jsonify(utils.get_projeto_info(id_projeto)), 200


@blueprint.route("/projeto/<id_projeto>/get_log", methods=["GET"])
@login_required
@utils.has_projeto_access
def get_projeto_log(id_projeto: str):
    return jsonify(utils.get_projeto_log(id_projeto)), 200

@blueprint.route("/projeto/<id_projeto>/get_credenciais", methods=["GET"])
@login_required
@utils.has_projeto_access
def get_projeto_credenciais(id_projeto: str):
    return jsonify(utils.get_projeto_credenciais(id_projeto)), 200

@blueprint.route("/projeto/<id_projeto>/set_credencial", methods=["POST"])
@login_required
@utils.has_projeto_access
def set_projeto_credencial(id_projeto: str):
    try:
        utils.set_projeto_credencial(id_projeto,credencial=request.get_json())
        return jsonify({"message": "Credencial alterada com sucesso"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@blueprint.route("/projeto/<id_projeto>/command/<command>", methods=["POST"])
@login_required
@utils.has_projeto_access
def set_projeto_command(id_projeto: str, command: str):
    try:
        return jsonify({"message": utils.set_projeto_command(id_projeto, command)}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@blueprint.route("/projeto/<id_projeto>/get_template")
@login_required
@utils.has_projeto_access
def get_projeto_template(id_projeto):
    template_path = utils.get_projeto_template(id_projeto)
    return send_file(
        template_path,
        as_attachment=True,
        download_name=f"{id_projeto}_{template_path.name}",
    )


@blueprint.route("/projeto/<id_projeto>/static/<filename>", methods=["GET"])
@login_required
@utils.has_projeto_access
def get_projeto_static(id_projeto, filename):
    return send_file(
        utils.get_projeto_static(id_projeto, filename), download_name=filename
    )


# Projeto Carga
@blueprint.route("/projeto/<id_projeto>/carga/get_carga/<status>", methods=["GET"])
@login_required
def get_projeto_carga(id_projeto: str, status: str):
    return jsonify(utils.get_projeto_carga(id_projeto, status)), 200


@blueprint.route("/projeto/<id_projeto>/carga/get_cargas", methods=["GET"])
@login_required
def get_projeto_cargas(id_projeto: str):
    return jsonify(utils.get_projeto_cargas(id_projeto)), 200

@blueprint.route("/projeto/<id_projeto>/carga/get_relatorio/<id_carga>")
@login_required
@utils.has_projeto_access
def get_projeto_carga_relatorio(id_projeto: str, id_carga: str):
    result = utils.get_projeto_carga_relatorio(id_projeto, id_carga)

    # compat: se utils ainda retornar só o buffer
    if isinstance(result, tuple):
        kind, buffer = result
    else:
        kind, buffer = "excel", result

    if kind == "zip":
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"{id_projeto}_relatorio_{id_carga}.zip",
            mimetype="application/zip",
        )

    # default: excel
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{id_projeto}_relatorio_{id_carga}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@blueprint.route("/projeto/<id_projeto>/carga/set_carga", methods=["POST"])
@login_required
@utils.has_projeto_access
def set_projeto_queue(id_projeto):
    file = request.files.get("file")
    if file:
        try:
            utils.set_projeto_carga(id_projeto, io.BytesIO(file.read()), file_name=file.filename)
            return jsonify({"message": "Carga importada com sucesso"}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    return jsonify({"message": "Nenhum arquivo encontrado"}), 400


@blueprint.route("/projeto/<id_projeto>/carga/clear_carga_erros", methods=["POST"])
@login_required
@utils.has_projeto_access
def clear_projeto_carga_erros(id_projeto):
    try:
        utils.clear_projeto_carga_erros(id_projeto)
        return jsonify({"message": "Erros limpados com sucesso"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


# Projeto Input
@blueprint.route("/projeto/<id_projeto>/input/get_input", methods=["GET"])
@login_required
@utils.has_projeto_access
def get_projeto_input(id_projeto):
    params = utils.get_projeto_input(id_projeto)
    if params is not None:
        return jsonify({"params": params}), 200
    return jsonify({}), 204


@blueprint.route("/projeto/<id_projeto>/input/set_response", methods=["POST"])
@login_required
@utils.has_projeto_access
def set_projeto_response(id_projeto):
    try:
        utils.set_projeto_response(id_projeto, request.data.decode('utf-8'))
        return jsonify({}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
