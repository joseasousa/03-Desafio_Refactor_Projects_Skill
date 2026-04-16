import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')


def require_secret_key(app):
    if app.config.get('SECRET_KEY'):
        return
    app.config['SECRET_KEY'] = os.urandom(32).hex()
