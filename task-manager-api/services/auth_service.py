from itsdangerous import URLSafeTimedSerializer
from flask import current_app


def generate_token(user):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps({'user_id': user.id, 'role': user.role}, salt='auth-token')
