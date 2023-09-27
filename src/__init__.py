import os
import psycopg2
from flask import Flask

app = Flask(__name__, template_folder='../templates')
__all__ = app  # Доступ на уровне пакета
#DATABASE_URL = os.getenv('DATABASE_URL')
#connection = psycopg2.connect(DATABASE_URL)
