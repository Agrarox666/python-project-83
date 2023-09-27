import datetime
import os

import psycopg2

from src import app, DATABASE_URL
from flask import render_template, request, redirect, url_for
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
            'index_error.html'
        )
    list_of_urls = get_all_urls()
    if tuple(input_url) not in list_of_urls or list_of_urls == []:
        save_url(input_url)
        print('SAAAAAVE')
    id = len(list_of_urls) + 1
    return redirect(url_for('show_url', id=id), 302)


@app.route('/urls')
def show_urls():
    return 'It will be urls here'


@app.route('/urls/<int:id>')
def show_url(id):
    url, date = get_url(id)
    return render_template(
        'show.html',
        id=id,
        url=url,
        date=date,
    )


def validate_url(input_url):
    return True if url(input_url) else False


def save_url(input_url):
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute("""
        INSERT INTO urls (name, created_at) VALUES (%s, %s);
        """, (input_url, datetime.date.today(),))
        print('execute???')


def get_url(id):
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute('SELECT name, created_at FROM urls WHERE id = %s;', (id,),)
        url = curs.fetchone()
        if url is None:
            return [None, None]
        return list(url)


def get_all_urls():
    connection = psycopg2.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute('SELECT name FROM urls;')
        return curs.fetchall()
