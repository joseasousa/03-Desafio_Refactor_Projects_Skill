def serialize_user(user, include_task_count=False, include_tasks=False, tasks=None):
    data = user.to_dict()

    if include_task_count:
        data['task_count'] = len(user.tasks)

    if include_tasks:
        data['tasks'] = [task.to_dict() for task in (tasks or user.tasks)]

    return data
