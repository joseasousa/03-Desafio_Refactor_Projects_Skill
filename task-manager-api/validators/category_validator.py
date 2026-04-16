from validators.constants import DEFAULT_COLOR


def parse_category_payload(data, partial=False):
    if not data:
        return None, 'Dados inválidos'

    result = {}

    if not partial or 'name' in data:
        name = data.get('name')
        if not name:
            return None, 'Nome é obrigatório'
        result['name'] = name

    if 'description' in data:
        result['description'] = data['description']
    elif not partial:
        result['description'] = ''

    if 'color' in data:
        result['color'] = data['color']
    elif not partial:
        result['color'] = DEFAULT_COLOR

    return result, None
