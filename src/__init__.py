from flask import Flask

app = Flask(__name__, template_folder='../templates')
__all__ = app  # Доступ на уровне пакета
