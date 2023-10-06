import os
import requests
from dotenv import load_dotenv
from flask import (render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   get_flashed_messages, Flask)
from page_analyzer.db import (get_all_urls,
                              save_url,
                              get_id_by_url,
                              get_all_sites,
                              get_site_by_id,
                              get_checks,
                              connection_to_db,
                              get_url_by_id)
from page_analyzer.seo_checker import check_seo
from page_analyzer.validator import validate_url, normalize_url


index = 'index.html'
show = 'show.html'
show_all = 'show_all.html'
app = Flask(__name__)
load_dotenv()
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def handler():
    return render_template(
        index,
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
        return render_template(index), 422
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
def checks(id):
    conn = connection_to_db()
    with conn.cursor() as curs:
        try:
            url = get_url_by_id(id)
            seo = check_seo(url)
            if seo['status_code'] != 200:
                raise requests.RequestException
            params = (id, seo['status_code'],
                      seo['h1'], seo['title'], seo['description'],
                      seo['created_at'],)
            query = '''INSERT INTO url_checks
                (url_id, status_code, h1, title, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s);'''
            curs.execute(query, params)

            conn.commit()
        except requests.RequestException:
            flash('Произошла ошибка при проверке', 'error')
            redirect(url_for('show_url', id=id))

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('show_url', id=id), 302)


@app.errorhandler(422)
def handler422(message):
    print(message)
    message = get_flashed_messages(with_categories=True)
    return render_template(
        index,
        message=message,
    )
