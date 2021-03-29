import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TESTING = True
DEBUG = True
FLASK_ENV = os.environ.get('FLASK_ENV')
SECRET_KEY = os.environ.get('SECRET_KEY')

SQLALCHEMY_TRACK_MODIFICATIONS = False

username = os.environ.get('DB_USERNAME')
password = os.environ.get('DB_PASSWORD')

url = 'localhost'
if 'DB_PORT' in os.environ:
    url += ':' + os.environ.get('DB_PORT')

name = os.environ.get('DB_NAME')

SQLALCHEMY_DATABASE_URI = f'postgresql://{username}:{password}@{url}/{name}'
