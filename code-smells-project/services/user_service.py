from models import criar_usuario as create_user_record
from models import login_usuario


def create_user(payload):
    if not payload:
        return None, "Dados inválidos"

    name = payload.get("nome", "")
    email = payload.get("email", "")
    password = payload.get("senha", "")
    if not name or not email or not password:
        return None, "Nome, email e senha são obrigatórios"

    return {"id": create_user_record(name, email, password)}, None


def login(payload):
    if not payload:
        return None, "Email e senha são obrigatórios"

    email = payload.get("email", "")
    password = payload.get("senha", "")
    if not email or not password:
        return None, "Email e senha são obrigatórios"

    user = login_usuario(email, password)
    if not user:
        return None, "Email ou senha inválidos"
    return user, None


criar_usuario = create_user
