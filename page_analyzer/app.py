from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    get_flashed_messages,
)
import os
import psycopg2
import validators
from dotenv import load_dotenv
from datetime import date
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template(
        'home.html',
    )


@app.post('/urls')
def url_post():
    data_dict = request.form.to_dict()
    data = data_dict['url']
    if not data:
        flash('URL обязателен', 'danger')
    elif validators.url(data) and len(data) <= 255:
        time = date.today()
        with conn.cursor() as curs:
            url_parse = urlparse(data)
            data = url_parse.scheme + '://' + url_parse.hostname
            curs.execute('SELECT id, name FROM urls WHERE name=%s', (data,))
            url = curs.fetchone()
            if url is not None:
                flash('Страница уже существует', 'info')
                return redirect(url_for('page_url', id=url[0]))
            else:
                curs.execute("""INSERT INTO urls (name, created_at)
                                VALUES (%s, %s)""",
                             (data, time))
                flash('Страница успешно добавлена', 'success')
                curs.execute('SELECT id FROM urls WHERE name=%s', (data,))
                id_new = curs.fetchone()
                return redirect(url_for('page_url', id=id_new[0]))
    else:
        flash('Некорректный URL', 'danger')
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'home.html',
        messages=messages
    ), 422


@app.route('/urls/<id>')
def page_url(id):
    with conn.cursor() as curs:
        messages = get_flashed_messages(with_categories=True)
        curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
        url = curs.fetchone()
        curs.execute("""SELECT * FROM url_checks WHERE url_id=%s
                        ORDER BY id DESC""", (id,))
        url_checks = curs.fetchall()
        if url_checks is None:
            return render_template(
                'url.html',
                id_url=url[0],
                name=url[1],
                time=url[2],
                messages=messages,
            )
        return render_template(
            'url.html',
            id_url=url[0],
            name=url[1],
            time=url[2],
            url_checks=url_checks,
            messages=messages,
        )


@app.route('/urls')
def urls():
    with conn.cursor() as curs:
        curs.execute("""SELECT DISTINCT ON (urls.id) urls.id AS url_id, name,
        url_checks.created_at AS created_at, status_code
        FROM urls LEFT JOIN url_checks ON urls.id = url_checks.url_id
        ORDER BY urls.id DESC""")
        urls = curs.fetchall()
        return render_template(
            'urls.html',
            urls=urls,
        )


@app.post('/urls/<id>/checks')
def checks(id):
    with conn.cursor() as curs:
        curs.execute('SELECT id, name FROM urls WHERE id=%s', (id,))

        url = curs.fetchone()

    try:
        time = date.today()
        r = requests.get(url[1])
        code = r.status_code
    except requests.RequestException:
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('page_url', id=url[0]))
    if code == requests.codes.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        if soup.h1:
            h1 = soup.h1.get_text()
        else:
            h1 = ''
        if soup.title:
            title = soup.title.get_text()
        else:
            title = ''
        atrmeta = soup.find_all("meta", attrs={"name": "description",
                                               "content": True})
        if atrmeta == []:
            meta = ''
        else:
            soup1 = BeautifulSoup(str(atrmeta[0]), 'html.parser')
            meta = soup1.meta['content']
        with conn.cursor() as curs:
            curs.execute("""INSERT INTO url_checks (url_id,
                                status_code, h1, title, description, created_at)
                                VALUES(%s, %s, %s, %s, %s, %s)""",
                     (url[0], code, h1, title, meta, time))
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('page_url', id=url[0]))




if __name__ == "__main__":
    app.run(debug=True)


