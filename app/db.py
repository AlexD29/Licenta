# db.py
import psycopg2
from flask import g

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname="Licenta",
            user="postgres",
            password="password",
            host="localhost"
        )
        return conn
    except Exception as e:
        print("Error connecting to the database:", e)
        return None

def before_request():
    g.db_conn = get_db_connection()
    if g.db_conn is not None:
        g.db_cursor = g.db_conn.cursor()
    else:
        g.db_cursor = None

def after_request(response):
    db_cursor = getattr(g, 'db_cursor', None)
    db_conn = getattr(g, 'db_conn', None)
    if db_cursor is not None:
        db_cursor.close()
    if db_conn is not None:
        db_conn.close()
    return response
