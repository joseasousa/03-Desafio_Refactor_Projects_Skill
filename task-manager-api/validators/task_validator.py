from datetime import datetime

from validators.constants import (
    DATE_FORMAT,
    DEFAULT_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_TITLE_LENGTH,
    VALID_STATUSES,
)


def parse_task_payload(data, partial=False):
    if not data:
        return None, 'Dados inválidos'

    result = {}

    if not partial or 'title' in data:
        title = data.get('title')
        if not title:
            return None, 'Título é obrigatório' if not partial else 'Título não pode ser vazio'
        if len(title) < MIN_TITLE_LENGTH:
            return None, 'Título muito curto'
        if len(title) > MAX_TITLE_LENGTH:
            return None, 'Título muito longo'
        result['title'] = title

    if 'description' in data:
        result['description'] = data['description']
    elif not partial:
        result['description'] = ''

    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return None, 'Status inválido'
        result['status'] = data['status']
    elif not partial:
        result['status'] = 'pending'

    if 'priority' in data:
        try:
            priority = int(data['priority'])
        except (TypeError, ValueError):
            return None, 'Prioridade inválida'
        if priority < 1 or priority > 5:
            return None, 'Prioridade deve ser entre 1 e 5'
        result['priority'] = priority
    elif not partial:
        result['priority'] = DEFAULT_PRIORITY

    for key in ('user_id', 'category_id'):
        if key in data:
            result[key] = data[key]
        elif not partial:
            result[key] = None

    if 'due_date' in data:
        if data['due_date']:
            try:
                result['due_date'] = datetime.strptime(data['due_date'], DATE_FORMAT)
            except (TypeError, ValueError):
                return None, 'Formato de data inválido. Use YYYY-MM-DD'
        else:
            result['due_date'] = None

    if 'tags' in data:
        result['tags'] = ','.join(data['tags']) if type(data['tags']) == list else data['tags']

    return result, None
