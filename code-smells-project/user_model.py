from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db


def get_todos_usuarios():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM usuarios")
    return [_usuario_to_dict(row) for row in cursor.fetchall()]


def get_usuario_por_id(usuario_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    row = cursor.fetchone()
    return _usuario_to_dict(row) if row else None


def criar_usuario(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, generate_password_hash(senha), tipo),
    )
    db.commit()
    return cursor.lastrowid


def login_usuario(email, senha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    if not row or not _senha_valida(row["senha"], senha):
        return None

    if row["senha"] == senha:
        cursor.execute(
            "UPDATE usuarios SET senha = ? WHERE id = ?",
            (generate_password_hash(senha), row["id"]),
        )
        db.commit()

    return _usuario_login_to_dict(row)


def _senha_valida(senha_armazenada, senha_informada):
    if not senha_armazenada:
        return False
    if senha_armazenada == senha_informada:
        return True
    return check_password_hash(senha_armazenada, senha_informada)


def _usuario_to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def _usuario_login_to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }
