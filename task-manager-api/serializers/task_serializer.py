def serialize_task(task, include_names=False):
    data = task.to_dict()
    data['overdue'] = task.is_overdue()

    if include_names:
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None

    return data


def serialize_task_summary(task):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'created_at': str(task.created_at),
        'due_date': str(task.due_date) if task.due_date else None,
        'overdue': task.is_overdue(),
    }
