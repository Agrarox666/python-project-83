import os

from dotenv import load_dotenv
from flask import Flask


app = Flask(__name__, template_folder='../templates')
app.secret_key = 'the random string'

index = 'index.html'
show = 'show.html'
show_all = 'show_all.html'
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
__all__ = ['app', 'index', 'show_all', 'show', 'DATABASE_URL']  # Доступ на уровне пакета
