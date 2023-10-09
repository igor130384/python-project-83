import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def connect_to_db():
    return psycopg2.connect(DATABASE_URL)


connect_to_db().autocommit = True


def get_name(data):
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT id, name FROM urls WHERE name=%s', (data,))
            url = curs.fetchone()
            return url


def add_date_time(data, time):
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute("""INSERT INTO urls (name, created_at)
                                            VALUES (%s, %s)""",
                         (data, time))


def get_id(data):
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT id FROM urls WHERE name=%s', (data,))
            id_new = curs.fetchone()
            return id_new


def get_id_url(id):
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
            url = curs.fetchone()

            curs.execute("""SELECT * FROM url_checks WHERE url_id=%s
                                ORDER BY id DESC""", (id,))
            url_checks = curs.fetchall()
            return url, url_checks


def get_add_data():
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute("""SELECT DISTINCT ON (urls.id) urls.id AS url_id, name,
            url_checks.created_at AS created_at, status_code
            FROM urls LEFT JOIN url_checks ON urls.id = url_checks.url_id
            ORDER BY urls.id DESC""")
            urls = curs.fetchall()
            return urls


def get_url(id):
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute('SELECT id, name FROM urls WHERE id=%s', (id,))
            url = curs.fetchone()
            return url


def add_data(url, code, h1, title, meta, time):
    with connect_to_db() as conn:
        with conn.cursor() as curs:
            curs.execute("""INSERT INTO url_checks (url_id,
                                status_code, h1, title, description, created_at)
                                    VALUES(%s, %s, %s, %s, %s, %s)""",
                         (url[0], code, h1, title, meta, time))
