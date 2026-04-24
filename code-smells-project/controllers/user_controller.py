from flask import jsonify

import models
import services
from .common import json_body, server_error


def listar_usuarios():
    try:
        return jsonify({"dados": models.get_todos_usuarios(), "sucesso": True}), 200
    except Exception as error:
        return server_error(error)


def buscar_usuario(id):
    try:
        user = models.get_usuario_por_id(id)
        if not user:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify({"dados": user, "sucesso": True}), 200
    except Exception as error:
        return server_error(error)


def criar_usuario():
    try:
        data, error = services.criar_usuario(json_body())
        if error:
            return jsonify({"erro": error}), 400
        return jsonify({"dados": data, "sucesso": True}), 201
    except Exception as error:
        return server_error(error)


def login():
    try:
        user, error = services.login(json_body())
        if error:
            status = 400 if error == "Email e senha são obrigatórios" else 401
            payload = {"erro": error}
            if status == 401:
                payload["sucesso"] = False
            return jsonify(payload), status
        return jsonify({"dados": user, "sucesso": True, "mensagem": "Login OK"}), 200
    except Exception as error:
        return server_error(error)
