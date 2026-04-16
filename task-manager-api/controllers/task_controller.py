from sqlalchemy.orm import joinedload

from database import db
from models.category import Category
from models.task import Task
from models.user import User
from serializers.task_serializer import serialize_task
from validators.task_validator import parse_task_payload


def list_tasks():
    tasks = (
        Task.query.options(joinedload(Task.user), joinedload(Task.category))
        .all()
    )
    return [serialize_task(task, include_names=True) for task in tasks], 200


def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    return serialize_task(task), 200


def create_task(data):
    values, error = parse_task_payload(data)
    if error:
        return {'error': error}, 400

    related_error = _validate_related(values)
    if related_error:
        return related_error

    task = Task(**values)

    try:
        db.session.add(task)
        db.session.commit()
        print(f"Task criada: {task.id} - {task.title}")
        return task.to_dict(), 201
    except Exception as exc:
        db.session.rollback()
        print(f"Erro ao criar task: {str(exc)}")
        return {'error': 'Erro ao criar task'}, 500


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    values, error = parse_task_payload(data, partial=True)
    if error:
        return {'error': error}, 400

    related_error = _validate_related(values)
    if related_error:
        return related_error

    for key, value in values.items():
        setattr(task, key, value)

    try:
        db.session.commit()
        print(f"Task atualizada: {task.id}")
        return task.to_dict(), 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao atualizar'}, 500


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404

    try:
        db.session.delete(task)
        db.session.commit()
        print(f"Task deletada: {task_id}")
        return {'message': 'Task deletada com sucesso'}, 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao deletar'}, 500


def search_tasks(args):
    query = args.get('q', '')
    status = args.get('status', '')
    priority = args.get('priority', '')
    user_id = args.get('user_id', '')

    tasks = Task.query

    if query:
        tasks = tasks.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%')
            )
        )

    if status:
        tasks = tasks.filter(Task.status == status)

    if priority:
        try:
            tasks = tasks.filter(Task.priority == int(priority))
        except ValueError:
            return {'error': 'Prioridade inválida'}, 400

    if user_id:
        try:
            tasks = tasks.filter(Task.user_id == int(user_id))
        except ValueError:
            return {'error': 'Usuário inválido'}, 400

    return [task.to_dict() for task in tasks.all()], 200


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()
    overdue_count = sum(1 for task in Task.query.all() if task.is_overdue())

    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }, 200


def _validate_related(values):
    if values.get('user_id'):
        if not User.query.get(values['user_id']):
            return {'error': 'Usuário não encontrado'}, 404

    if values.get('category_id'):
        if not Category.query.get(values['category_id']):
            return {'error': 'Categoria não encontrada'}, 404

    return None
