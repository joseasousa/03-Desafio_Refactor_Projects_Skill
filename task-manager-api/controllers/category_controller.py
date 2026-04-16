from database import db
from models.category import Category
from models.task import Task
from validators.category_validator import parse_category_payload


def list_categories():
    categories = Category.query.all()
    result = []
    for category in categories:
        data = category.to_dict()
        data['task_count'] = Task.query.filter_by(category_id=category.id).count()
        result.append(data)
    return result, 200


def create_category(data):
    values, error = parse_category_payload(data)
    if error:
        return {'error': error}, 400

    category = Category(**values)

    try:
        db.session.add(category)
        db.session.commit()
        return category.to_dict(), 201
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao criar categoria'}, 500


def update_category(category_id, data):
    category = Category.query.get(category_id)
    if not category:
        return {'error': 'Categoria não encontrada'}, 404

    values, error = parse_category_payload(data, partial=True)
    if error:
        return {'error': error}, 400

    for key, value in values.items():
        setattr(category, key, value)

    try:
        db.session.commit()
        return category.to_dict(), 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao atualizar'}, 500


def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return {'error': 'Categoria não encontrada'}, 404

    try:
        db.session.delete(category)
        db.session.commit()
        return {'message': 'Categoria deletada'}, 200
    except Exception:
        db.session.rollback()
        return {'error': 'Erro ao deletar'}, 500
