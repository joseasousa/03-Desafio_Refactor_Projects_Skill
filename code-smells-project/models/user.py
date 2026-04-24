from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db


def get_all_users():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM usuarios")
    return [_user_to_dict(row) for row in cursor.fetchall()]


def get_user_by_id(user_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    return _user_to_dict(row) if row else None


def create_user(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, generate_password_hash(senha), tipo),
    )
    db.commit()
    return cursor.lastrowid


def authenticate_user(email, senha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    if not row or not _password_matches(row["senha"], senha):
        return None

    if row["senha"] == senha:
        cursor.execute(
            "UPDATE usuarios SET senha = ? WHERE id = ?",
            (generate_password_hash(senha), row["id"]),
        )
        db.commit()

    return _login_user_to_dict(row)


def _password_matches(stored_password, provided_password):
    if not stored_password:
        return False
    if stored_password == provided_password:
        return True
    return check_password_hash(stored_password, provided_password)


def _user_to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def _login_user_to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
    }


get_todos_usuarios = get_all_users
get_usuario_por_id = get_user_by_id
criar_usuario = create_user
login_usuario = authenticate_user
