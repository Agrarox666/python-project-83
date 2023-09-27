from src import app
from flask import render_template, request, redirect
from validators import url

app = app


@app.route('/')
def handler():
    return render_template(
        'index.html')


@app.route('/urls', methods=['POST'])
def handler_form():
    input_url = request.form.to_dict()['url']
    error = validate_url(input_url)
    if error:
        return render_template(
            'index_error.html'
        )
    return f'It will be url(id) here. Current url is {input_url}'


@app.route('/urls')
def show_urls():
    return 'It will be urls here'


def validate_url(input_url):
    if url(input_url):
        return False
    else:
        return True
