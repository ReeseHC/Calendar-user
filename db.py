import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()
from flask import g

db_params = {
  'database': 'Doctor\'s Office DB',
  'user': 'postgres',
  'password': os.environ['DB_PASSWORD'],
  'host': os.environ['DB_HOST'],
  'port': 5432
}

def get_db():
    if 'db' not in g:
        g.db_conn = psycopg2.connect(**db_params)
        g.db_conn.set_session(autocommit=True)
        g.db = g.db_conn.cursor(cursor_factory=RealDictCursor)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close() 


def init_app(app):
    app.teardown_appcontext(close_db)
