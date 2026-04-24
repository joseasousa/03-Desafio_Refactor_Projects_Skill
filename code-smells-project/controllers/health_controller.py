from flask import jsonify

from database import get_db


def health_check():
    try:
        cursor = get_db().cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception:
        return jsonify({"status": "erro"}), 500
