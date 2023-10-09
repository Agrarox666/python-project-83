from datetime import datetime

from psycopg2 import extras

from page_analyzer.app import connection_to_db


def get_checks(url_id):
    query = '''SELECT id, status_code, h1, title, description, created_at
    FROM url_checks
    WHERE url_id=%s ORDER BY created_at DESC, id DESC;'''
    conn = connection_to_db()
    with (conn.cursor(cursor_factory=extras.RealDictCursor)as curs):
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
