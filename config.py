import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TESTING = True
DEBUG = True
FLASK_ENV = os.environ.get('FLASK_ENV')
SECRET_KEY = os.environ.get('SECRET_KEY')
