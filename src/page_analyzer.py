from src import app

app = app


@app.route('/')
def handler():
    return 'Hello third project!'


@app.route('/show/<id>')
def get_show(ids):
    return f'Show me your{ids}'
