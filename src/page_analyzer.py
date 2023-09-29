from datetime import datetime

import psycopg2

from src import app, DATABASE_URL
from flask import render_template, request, redirect, url_for, flash, get_flashed_messages
from validators import url

app = app


@app.route('/')
def handler():
    return render_template(
        'index.html')


@app.route('/urls', methods=['POST'])
def handler_form():
    input_url = request.form.to_dict()['url']
    error = not validate_url(input_url)
    if error:
        return render_template(
            'index.html',
            error=error,
        ), 422

    if (input_url,) not in get_all_urls():
        save_url(input_url)
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'info')

    id = get_id_by_url(input_url)
    return redirect(url_for('show_url', id=id), 302)


@app.route('/urls')
def show_urls():
    sites = get_all_sites()
    return render_template(
        'show_all.html',
        sites=sites,
    )


@app.route('/urls/<int:id>')
def show_url(id):
    url, date = get_url_by_id(id)
    message = get_flashed_messages(with_categories=True)
    print(message)
    return render_template(
        'show.html',
        id=id,
        url=url,
        date=date,
        message=message,
    )


def validate_url(input_url):
    return True if url(input_url) else False


def save_url(input_url):
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s);',
                     (input_url, datetime.now(),))
        connection.commit()


def get_url_by_id(id):
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute('SELECT name, created_at FROM urls WHERE id = %s;', (id,), )
        url = curs.fetchone()
        if url is None:
            return [None, None]
        return list(url)


def get_id_by_url(input_url):
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute('SELECT id FROM urls WHERE name=%s;', (input_url,))
        return curs.fetchone()[0]

def get_all_urls():
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute('SELECT name FROM urls;')
        return curs.fetchall()


def get_all_sites():
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute('SELECT * FROM urls ORDER BY created_at DESC, id DESC;')
        return curs.fetchall()
