from flask import current_app, jsonify, request

import controllers
from database import reset_db


def register_routes(app):
    app.add_url_rule("/produtos", "listar_produtos", controllers.listar_produtos, methods=["GET"])
    app.add_url_rule("/produtos/busca", "buscar_produtos", controllers.buscar_produtos, methods=["GET"])
    app.add_url_rule("/produtos/<int:id>", "buscar_produto", controllers.buscar_produto, methods=["GET"])
    app.add_url_rule("/produtos", "criar_produto", controllers.criar_produto, methods=["POST"])
    app.add_url_rule("/produtos/<int:id>", "atualizar_produto", controllers.atualizar_produto, methods=["PUT"])
    app.add_url_rule("/produtos/<int:id>", "deletar_produto", controllers.deletar_produto, methods=["DELETE"])

    app.add_url_rule("/usuarios", "listar_usuarios", controllers.listar_usuarios, methods=["GET"])
    app.add_url_rule("/usuarios/<int:id>", "buscar_usuario", controllers.buscar_usuario, methods=["GET"])
    app.add_url_rule("/usuarios", "criar_usuario", controllers.criar_usuario, methods=["POST"])
    app.add_url_rule("/login", "login", controllers.login, methods=["POST"])

    app.add_url_rule("/pedidos", "criar_pedido", controllers.criar_pedido, methods=["POST"])
    app.add_url_rule("/pedidos", "listar_todos_pedidos", controllers.listar_todos_pedidos, methods=["GET"])
    app.add_url_rule("/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", controllers.listar_pedidos_usuario, methods=["GET"])
    app.add_url_rule("/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", controllers.atualizar_status_pedido, methods=["PUT"])

    app.add_url_rule("/relatorios/vendas", "relatorio_vendas", controllers.relatorio_vendas, methods=["GET"])
    app.add_url_rule("/health", "health_check", controllers.health_check, methods=["GET"])
    app.add_url_rule("/", "index", index, methods=["GET"])
    app.add_url_rule("/admin/reset-db", "reset_database", reset_database, methods=["POST"])
    app.add_url_rule("/admin/query", "executar_query", executar_query, methods=["POST"])


def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


def reset_database():
    error = _validate_admin()
    if error:
        return error
    reset_db()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


def executar_query():
    return jsonify({"erro": "Execução arbitrária de SQL desabilitada"}), 403


def _validate_admin():
    if not current_app.config["ENABLE_ADMIN_ENDPOINTS"]:
        return jsonify({"erro": "Endpoint administrativo desabilitado"}), 403

    token = current_app.config.get("ADMIN_TOKEN")
    if not token or request.headers.get("X-Admin-Token") != token:
        return jsonify({"erro": "Não autorizado"}), 401
    return None
