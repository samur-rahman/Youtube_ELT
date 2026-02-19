from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import RealDictCursor


def getConnCursor():
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_eld", database="elt_db")
    conn = hook.get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    return conn, cur


def closeConnCursor(conn, cur):
    cur.close()
    conn.close()