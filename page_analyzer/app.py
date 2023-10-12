import os
from datetime import datetime

import psycopg2
import requests
from dotenv import load_dotenv
from flask import (render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   get_flashed_messages, Flask)
from psycopg2 import extras
from requests import HTTPError

from page_analyzer.page_checker import check_page
from page_analyzer.validator import validate_url, normalize_url

app = Flask(__name__)
load_dotenv()
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')


def connection_to_db():
    db = app.config['DATABASE_URL']
    connection = psycopg2.connect(db)
    return connection


@app.route('/')
def handler():
    return render_template(
        'main.html',
    )


@app.route('/urls', methods=['POST'])
def handler_form():
    input_url = request.form.to_dict()['url']
    error = not validate_url(input_url)
    if error:
        if input_url == '':
            flash('URL обязателен', 'danger')
        else:
            flash('Некорректный URL', 'danger')
        return render_template('main.html'), 422
    normalized_url = normalize_url(input_url)

    if (normalized_url,) not in get_all_urls():
        save_url(normalized_url)
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'info')

    id = get_id_by_url(normalized_url)
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
    site = get_site_by_id(id)
    url = site['name']
    date = site['created_at']
    message = get_flashed_messages(with_categories=True)
    return render_template(
        'show.html',
        id=id,
        url=url,
        date=date,
        message=message,
        checks=get_checks(id),
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def checks(id):
    conn = connection_to_db()
    with conn.cursor() as curs:
        try:
            url = get_url_by_id(id)
            check_result = check_page(url)
            params = (id, check_result['status_code'],
                      check_result['h1'], check_result['title'],
                      check_result['description'],
                      check_result['created_at'],)
            query = '''INSERT INTO url_checks
                (url_id, status_code, h1, title, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s);'''
            curs.execute(query, params)
            conn.commit()
        except (requests.RequestException, HTTPError):
            flash('Произошла ошибка при проверке', 'error')
            redirect(url_for('show_url', id=id))

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id=id), 302)


@app.errorhandler(404)
def handler404(message):
    return render_template(
        'errors/404.html',
        message=message,
    )


@app.errorhandler(422)
def handler422():
    message = get_flashed_messages(with_categories=True)
    return render_template(
        'main.html',
        message=message,
    )


@app.errorhandler(500)
def handler500(message):
    return render_template(
        'errors/500.html',
        message=message,
    )


def get_checks(url_id):
    query = '''SELECT id, status_code, h1, title, description, created_at
    FROM url_checks
    WHERE url_id=%s ORDER BY created_at DESC, id DESC;'''
    conn = connection_to_db()
    with (conn.cursor(cursor_factory=extras.RealDictCursor) as curs):
        curs.execute(query, (url_id,))
        checks = curs.fetchall()
    return checks


def save_url(input_url):
    conn = connection_to_db()
    with conn.cursor() as curs:
        curs.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s);',
                     (input_url, datetime.now(),))
        conn.commit()


def get_site_by_id(id):
    conn = connection_to_db()
    with conn.cursor(cursor_factory=extras.RealDictCursor) as curs:
        curs.execute('SELECT name, created_at FROM urls WHERE id = %s;',
                     (id,))
        site = curs.fetchone()
    return site


def get_url_by_id(id):
    conn = connection_to_db()
    with conn.cursor() as curs:
        curs.execute('SELECT name FROM urls WHERE id = %s;',
                     (id,), )
        return curs.fetchone()[0]


def get_id_by_url(input_url):
    conn = connection_to_db()
    with conn.cursor() as curs:
        curs.execute('SELECT id FROM urls WHERE name=%s;', (input_url,))
        return curs.fetchone()[0]


def get_all_urls():
    conn = connection_to_db()
    with conn.cursor() as curs:
        curs.execute('SELECT name FROM urls;')
        return curs.fetchall()


def get_all_sites():
    conn = connection_to_db()
    with conn.cursor(cursor_factory=extras.RealDictCursor) as curs:
        curs.execute('''
        SELECT id, name FROM urls ORDER BY created_at DESC, id DESC;''')
        sites = curs.fetchall()
    for site in sites:
        id = site['id']
        if get_checks(id):
            last_check = get_checks(id)[0]
            site['status_code'] = last_check['status_code']
            site['last_check'] = last_check['created_at']
    return sites
