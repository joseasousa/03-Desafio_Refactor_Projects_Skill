from flask import jsonify, request

import models
import services
from database import get_db


def listar_produtos():
    try:
        return jsonify({"dados": models.get_todos_produtos(), "sucesso": True}), 200
    except Exception as error:
        return _erro_servidor(error)


def buscar_produto(id):
    try:
        produto = models.get_produto_por_id(id)
        if not produto:
            return jsonify({"erro": "Produto não encontrado", "sucesso": False}), 404
        return jsonify({"dados": produto, "sucesso": True}), 200
    except Exception as error:
        return _erro_servidor(error)


def criar_produto():
    try:
        dados, erro = services.criar_produto(_json_body())
        if erro:
            return jsonify({"erro": erro}), 400
        return jsonify({"dados": dados, "sucesso": True, "mensagem": "Produto criado"}), 201
    except Exception as error:
        return _erro_servidor(error)


def atualizar_produto(id):
    try:
        sucesso, erro, status = services.atualizar_produto(id, _json_body())
        if not sucesso:
            return jsonify({"erro": erro}), status
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200
    except Exception as error:
        return _erro_servidor(error)


def deletar_produto(id):
    try:
        if not services.deletar_produto(id):
            return jsonify({"erro": "Produto não encontrado"}), 404
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
    except Exception as error:
        return _erro_servidor(error)


def buscar_produtos():
    try:
        preco_min, erro = _float_query("preco_min")
        if erro:
            return jsonify({"erro": erro}), 400
        preco_max, erro = _float_query("preco_max")
        if erro:
            return jsonify({"erro": erro}), 400

        resultados = models.buscar_produtos(
            request.args.get("q", ""),
            request.args.get("categoria"),
            preco_min,
            preco_max,
        )
        return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
    except Exception as error:
        return _erro_servidor(error)


def listar_usuarios():
    try:
        return jsonify({"dados": models.get_todos_usuarios(), "sucesso": True}), 200
    except Exception as error:
        return _erro_servidor(error)


def buscar_usuario(id):
    try:
        usuario = models.get_usuario_por_id(id)
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        return jsonify({"dados": usuario, "sucesso": True}), 200
    except Exception as error:
        return _erro_servidor(error)


def criar_usuario():
    try:
        dados, erro = services.criar_usuario(_json_body())
        if erro:
            return jsonify({"erro": erro}), 400
        return jsonify({"dados": dados, "sucesso": True}), 201
    except Exception as error:
        return _erro_servidor(error)


def login():
    try:
        usuario, erro = services.login(_json_body())
        if erro:
            status = 400 if erro == "Email e senha são obrigatórios" else 401
            payload = {"erro": erro}
            if status == 401:
                payload["sucesso"] = False
            return jsonify(payload), status
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
    except Exception as error:
        return _erro_servidor(error)


def criar_pedido():
    try:
        resultado, erro = services.criar_pedido(_json_body())
        if erro:
            return jsonify({"erro": erro, "sucesso": False}), 400
        return jsonify({
            "dados": resultado,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }), 201
    except Exception as error:
        return _erro_servidor(error)


def listar_pedidos_usuario(usuario_id):
    try:
        return jsonify({"dados": models.get_pedidos_usuario(usuario_id), "sucesso": True}), 200
    except Exception as error:
        return _erro_servidor(error)


def listar_todos_pedidos():
    try:
        return jsonify({"dados": models.get_todos_pedidos(), "sucesso": True}), 200
    except Exception as error:
        return _erro_servidor(error)


def atualizar_status_pedido(pedido_id):
    try:
        erro = services.atualizar_status_pedido(pedido_id, _json_body())
        if erro:
            return jsonify({"erro": erro}), 400
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
    except Exception as error:
        return _erro_servidor(error)


def relatorio_vendas():
    try:
        return jsonify({"dados": models.relatorio_vendas(), "sucesso": True}), 200
    except Exception as error:
        return _erro_servidor(error)


def health_check():
    try:
        cursor = get_db().cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception:
        return jsonify({"status": "erro"}), 500


def _json_body():
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else None


def _float_query(nome):
    valor = request.args.get(nome)
    if valor in (None, ""):
        return None, None
    try:
        return float(valor), None
    except ValueError:
        return None, nome + " inválido"


def _erro_servidor(error):
    return jsonify({"erro": str(error)}), 500
