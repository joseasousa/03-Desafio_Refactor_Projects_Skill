from flask import jsonify

import models
from .common import server_error


def relatorio_vendas():
    try:
        return jsonify({"dados": models.relatorio_vendas(), "sucesso": True}), 200
    except Exception as error:
        return server_error(error)
