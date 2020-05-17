import os

current_path = os.path.dirname(os.path.realpath(__file__))


class Config:
    DEBUG = False
    SECRET_KEY = os.environ.get('STEPIK_BONUS_CARDS_SECRET_KEY_API')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('STEPIK_BONUS_CARDS_JWT_SECRET_KEY')
