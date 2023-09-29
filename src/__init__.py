import os

from dotenv import load_dotenv
from flask import Flask


app = Flask(__name__, template_folder='../templates')
app.secret_key = 'the random string'
__all__ = app  # Доступ на уровне пакета
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
