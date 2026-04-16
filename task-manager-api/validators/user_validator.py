import re

from validators.constants import MIN_PASSWORD_LENGTH, VALID_ROLES


EMAIL_PATTERN = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'


def parse_user_payload(data, partial=False):
    if not data:
        return None, 'Dados inválidos'

    result = {}

    if not partial or 'name' in data:
        name = data.get('name')
        if not name:
            return None, 'Nome é obrigatório'
        result['name'] = name

    if not partial or 'email' in data:
        email = data.get('email')
        if not email:
            return None, 'Email é obrigatório'
        if not re.match(EMAIL_PATTERN, email):
            return None, 'Email inválido'
        result['email'] = email

    if not partial or 'password' in data:
        password = data.get('password')
        if not password:
            return None, 'Senha é obrigatória'
        if len(password) < MIN_PASSWORD_LENGTH:
            return None, 'Senha deve ter no mínimo 4 caracteres' if not partial else 'Senha muito curta'
        result['password'] = password

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            return None, 'Role inválido'
        result['role'] = data['role']
    elif not partial:
        result['role'] = 'user'

    if 'active' in data:
        result['active'] = data['active']

    return result, None
