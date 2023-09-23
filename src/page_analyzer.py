from src import app

app = app


@app.route('/')
def handler():
    return 'Hello third project!'
