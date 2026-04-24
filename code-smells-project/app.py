import os
import secrets

from flask import Flask
from flask_cors import CORS

from database import close_db, get_db
from routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    app.config["DEBUG"] = _env_bool("FLASK_DEBUG", False)
    app.config["DATABASE"] = os.environ.get("DATABASE", "loja.db")
    app.config["ADMIN_TOKEN"] = os.environ.get("ADMIN_TOKEN")
    app.config["ENABLE_ADMIN_ENDPOINTS"] = _env_bool("ENABLE_ADMIN_ENDPOINTS", False)

    CORS(app)
    app.teardown_appcontext(close_db)
    register_routes(app)
    return app


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
