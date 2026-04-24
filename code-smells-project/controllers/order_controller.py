from flask import jsonify

import models
import services
from .common import json_body, server_error


def criar_pedido():
    try:
        result, error = services.criar_pedido(json_body())
        if error:
            return jsonify({"erro": error, "sucesso": False}), 400
        return jsonify({
            "dados": result,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }), 201
    except Exception as error:
        return server_error(error)


def listar_pedidos_usuario(usuario_id):
    try:
        return jsonify({"dados": models.get_pedidos_usuario(usuario_id), "sucesso": True}), 200
    except Exception as error:
        return server_error(error)


def listar_todos_pedidos():
    try:
        return jsonify({"dados": models.get_todos_pedidos(), "sucesso": True}), 200
    except Exception as error:
        return server_error(error)


def atualizar_status_pedido(pedido_id):
    try:
        error = services.atualizar_status_pedido(pedido_id, json_body())
        if error:
            return jsonify({"erro": error}), 400
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
    except Exception as error:
        return server_error(error)
