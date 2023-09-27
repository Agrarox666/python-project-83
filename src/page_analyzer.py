from src import app
from flask import render_template

app = app


@app.route('/')
def handler():
    return render_template(
        'index.html')


@app.route('/show/<ids>')
def get_show(ids):
    return f'Show me your{ids}'
