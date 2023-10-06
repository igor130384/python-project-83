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
import datetime
import requests
from requests import ConnectionError, HTTPError

from page_analyzer.db_query import get_name, add_date_time, get_id, get_id_url,\
    get_add_data,\
    get_url,\
    add_data
from page_analyzer.page import get_content_of_page
from page_analyzer.url import pars_url

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
        time = datetime.date.today()
        pars_url()
        url = get_name(data)
        if url is not None:
            flash('Страница уже существует', 'info')
            return redirect(url_for('page_url', id=url[0]))
        else:
            add_date_time(data, time)
            flash('Страница успешно добавлена', 'success')
            id_new = get_id(data)
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
    messages = get_flashed_messages(with_categories=True)
    url, url_checks = get_id_url(id)
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
    urls = get_add_data()
    return render_template(
        'urls.html',
        urls=urls, )


@app.post('/urls/<id>/checks')
def checks(id):
    url = get_url(id)
    try:
        r = requests.get(url[1])
        r.raise_for_status()
    except (ConnectionError, HTTPError):
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('page_url', id=url[0]))

    h1, title, meta = get_content_of_page(r)
    code = r.status_code
    time = datetime.date.today()
    add_data(url, code, h1, title, meta, time)

    flash('Страница успешно проверена', 'success')
    return redirect(url_for('page_url', id=url[0]))


if __name__ == "__main__":
    app.run(debug=True)
