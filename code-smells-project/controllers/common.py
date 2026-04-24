from flask import jsonify, request


def json_body():
    payload = request.get_json(silent=True)
    return payload if isinstance(payload, dict) else None


def float_query(name):
    value = request.args.get(name)
    if value in (None, ""):
        return None, None
    try:
        return float(value), None
    except ValueError:
        return None, name + " inválido"


def server_error(error):
    return jsonify({"erro": str(error)}), 500
