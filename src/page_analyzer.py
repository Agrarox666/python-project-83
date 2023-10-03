from datetime import datetime
import psycopg
import requests
from src import DATABASE_URL, app, index, show_all, show
from flask import (render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   get_flashed_messages)
from bs4 import BeautifulSoup

from src.db import (get_checks, save_url, get_site_by_id,
                    get_url_by_id, get_id_by_url, get_all_urls, get_all_sites)
from src.validator import validate_url, normalize_url


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
            seo = check_seo(url)
            params = (id, seo['status_code'],
                      seo['h1'], seo['title'], seo['description'],
                      seo['created_at'],)
            query = '''INSERT INTO url_checks
            (url_id, status_code, h1, title, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s);'''
            curs.execute(query, params)

            connection.commit()
        except requests.RequestException:
            flash('Произошла ошибка при проверке', 'error')

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id=id), 302)


def check_seo(input_url):
    result = {'status_code': '',
              'h1': '',
              'title': '',
              'description': '',
              'created_at': '',
              }
    try:
        response = requests.get(input_url)
        result['status_code'] = response.status_code
        result['created_at'] = datetime.now().date()
        html_doc = response.content
        soup = BeautifulSoup(html_doc, 'html.parser')
        if soup.h1:
            result['h1'] = soup.h1.string
        if soup.title:
            result['title'] = soup.title.string
        meta = soup.find('meta', attrs={'name': 'description'})
        result['description'] = meta['content']

    except AttributeError as error:
        print(error)
    finally:
        return result
