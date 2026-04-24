from flask import jsonify, request

import models
import services
from .common import float_query, json_body, server_error


def listar_produtos():
    try:
        return jsonify({"dados": models.get_todos_produtos(), "sucesso": True}), 200
    except Exception as error:
        return server_error(error)


def buscar_produto(id):
    try:
        product = models.get_produto_por_id(id)
        if not product:
            return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404
        return jsonify({"dados": product, "sucesso": True}), 200
    except Exception as error:
        return server_error(error)


def criar_produto():
    try:
        data, error = services.criar_produto(json_body())
        if error:
            return jsonify({"erro": error}), 400
        return jsonify({"dados": data, "sucesso": True, "mensagem": "Produto criado"}), 201
    except Exception as error:
        return server_error(error)


def atualizar_produto(id):
    try:
        success, error, status = services.atualizar_produto(id, json_body())
        if not success:
            return jsonify({"erro": error}), status
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200
    except Exception as error:
        return server_error(error)


def deletar_produto(id):
    try:
        if not services.deletar_produto(id):
            return jsonify({"erro": "Produto não encontrado"}), 404
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
    except Exception as error:
        return server_error(error)


def buscar_produtos():
    try:
        min_price, error = float_query("preco_min")
        if error:
            return jsonify({"erro": error}), 400
        max_price, error = float_query("preco_max")
        if error:
            return jsonify({"erro": error}), 400

        results = models.buscar_produtos(
            request.args.get("q", ""),
            request.args.get("categoria"),
            min_price,
            max_price,
        )
        return jsonify({"dados": results, "total": len(results), "sucesso": True}), 200
    except Exception as error:
        return server_error(error)
