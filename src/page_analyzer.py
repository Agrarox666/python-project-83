from datetime import datetime
import psycopg
from psycopg.rows import dict_row
import requests
from src import *
from flask import (render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   get_flashed_messages)
from validators import url

app = app


@app.route('/')
def handler():
    return render_template(
        index)


@app.route('/urls', methods=['POST'])
def handler_form():
    input_url = request.form.to_dict()['url']
    error = not validate_url(input_url)
    if error:
        return render_template(
            index,
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
        show_all,
        sites=sites,
    )


@app.route('/urls/<int:id>')
def show_url(id):
    site = get_site_by_id(id)
    url = site['name']
    date = site['created_at']
    message = get_flashed_messages(with_categories=True)
    return render_template(
        show,
        id=id,
        url=url,
        date=date,
        message=message,
        checks=get_checks(id),
    )


@app.route('/urls/<int:id>/checks', methods=['POST'])
def check_url(id):
    connection = psycopg.connect(DATABASE_URL)
    with connection.cursor() as curs:
        try:
            url = get_url_by_id(id)
            response = requests.get(url)
            status_code = response.status_code
            curs.execute(
                '''INSERT INTO url_checks (url_id, status_code, created_at)
                VALUES (%s, %s, %s);''',
                (id, status_code, datetime.now(),))
            connection.commit()
        except requests.RequestException:
            flash('Произошла ошибка при проверке', 'error')

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id=id), 302)


def get_checks(url_id):
    connection = psycopg.connect(DATABASE_URL)
    with connection.cursor(row_factory=dict_row) as curs:
        curs.execute('''SELECT id, status_code, created_at FROM url_checks
        WHERE url_id=%s ORDER BY created_at DESC, id DESC;''', (url_id,))
        checks = curs.fetchall()
    return checks


def validate_url(input_url):
    return True if url(input_url) else False


def save_url(input_url):
    connection = psycopg.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s);',
                     (input_url, datetime.now(),))
        connection.commit()


def get_site_by_id(id):
    connection = psycopg.connect(DATABASE_URL)
    with connection.cursor(row_factory=dict_row) as curs:
        curs.execute('SELECT name, created_at FROM urls WHERE id = %s;',
                     (id,), )
        site = curs.fetchone()
    return site


def get_url_by_id(id):
    connection = psycopg.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute('SELECT name FROM urls WHERE id = %s;',
                     (id,), )
        return curs.fetchone()[0]


def get_id_by_url(input_url):
    connection = psycopg.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute('SELECT id FROM urls WHERE name=%s;', (input_url,))
        return curs.fetchone()[0]


def get_all_urls():
    connection = psycopg.connect(DATABASE_URL)
    with connection.cursor() as curs:
        curs.execute('SELECT name FROM urls;')
        return curs.fetchall()


def get_all_sites():
    connection = psycopg.connect(DATABASE_URL)
    with connection.cursor(row_factory=dict_row) as curs:
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
