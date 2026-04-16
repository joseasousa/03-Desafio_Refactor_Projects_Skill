from database import db
from models.task import Task
from models.user import User
from serializers.task_serializer import serialize_task_summary
from serializers.user_serializer import serialize_user
from services.auth_service import generate_token
from validators.user_validator import parse_user_payload


def list_users():
    users = User.query.all()
    return [serialize_user(user, include_task_count=True) for user in users], 200


def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    return serialize_user(user, include_tasks=True, tasks=tasks), 200


def create_user(data):
    values, error = parse_user_payload(data)
    if error:
        return {'error': error}, 400

    existing = User.query.filter_by(email=values['email']).first()
    if existing:
        return {'error': 'Email já cadastrado'}, 409

    user = User()
    _apply_user_values(user, values)

    try:
        db.session.add(user)
        db.session.commit()
        print(f"Usuário criado: {user.id} - {user.name}")
        return user.to_dict(), 201
    except Exception as exc:
        db.session.rollback()
        print(f"ERRO: {str(exc)}")
        return {'error': 'Erro ao criar usuário'}, 500


def update_user(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    values, error = parse_user_payload(data, partial=True)
    if error:
        return {'error': error}, 400

    if 'email' in values:
        existing = User.query.filter_by(email=values['email']).first()
        if existing and existing.id != user_id:
            return {'error': 'Email já cadastrado'}, 409

    _apply_user_values(user, values)

    try:
        db.session.commit()
        return user.to_dict(), 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao atualizar'}, 500


def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    for task in Task.query.filter_by(user_id=user_id).all():
        db.session.delete(task)

    try:
        db.session.delete(user)
        db.session.commit()
        print(f"Usuário deletado: {user_id}")
        return {'message': 'Usuário deletado com sucesso'}, 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao deletar'}, 500


def get_user_tasks(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'Usuário não encontrado'}, 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    return [serialize_task_summary(task) for task in tasks], 200


def login(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return {'error': 'Email e senha são obrigatórios'}, 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return {'error': 'Credenciais inválidas'}, 401

    if user.uses_legacy_password_hash():
        user.set_password(password)
        db.session.commit()

    if not user.active:
        return {'error': 'Usuário inativo'}, 403

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': generate_token(user),
    }, 200


def _apply_user_values(user, values):
    for key, value in values.items():
        if key == 'password':
            user.set_password(value)
        else:
            setattr(user, key, value)
