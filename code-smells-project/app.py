import os
import secrets

from flask import Flask, current_app, jsonify, request
from flask_cors import CORS

import controllers
from database import close_db, get_db, reset_db


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    app.config["DEBUG"] = _env_bool("FLASK_DEBUG", False)
    app.config["DATABASE"] = os.environ.get("DATABASE", "loja.db")
    app.config["ADMIN_TOKEN"] = os.environ.get("ADMIN_TOKEN")
    app.config["ENABLE_ADMIN_ENDPOINTS"] = _env_bool("ENABLE_ADMIN_ENDPOINTS", False)

    CORS(app)
    app.teardown_appcontext(close_db)
    _registrar_rotas(app)
    _registrar_admin(app)
    return app


def _registrar_rotas(app):
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


def _registrar_admin(app):
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
    erro = _validar_admin()
    if erro:
        return erro
    reset_db()
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200


def executar_query():
    return jsonify({"erro": "Execução arbitrária de SQL desabilitada"}), 403


def _validar_admin():
    if not current_app.config["ENABLE_ADMIN_ENDPOINTS"]:
        return jsonify({"erro": "Endpoint administrativo desabilitado"}), 403

    token = current_app.config.get("ADMIN_TOKEN")
    if not token or request.headers.get("X-Admin-Token") != token:
        return jsonify({"erro": "Não autorizado"}), 401
    return None


def _env_bool(nome, default):
    valor = os.environ.get(nome)
    if valor is None:
        return default
    return valor.lower() in {"1", "true", "yes", "on"}


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        get_db()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
