from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import RealDictCursor

table = "yt_api"


def getConnCursor():
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_eld", database="elt_db")
    conn = hook.get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    return conn, cur


def closeConnCursor(conn, cur):
    cur.close()
    conn.close()


def createSchema(schema):
    conn, cur = getConnCursor()

    schema_sql = f"CREATE SCHEMA IF NOT EXISTS {schema};"
    cur.execute(schema_sql)

    conn.commit()
    closeConnCursor(conn, cur)


def createTable(schema):
    conn, cur = getConnCursor()

    if schema == 'staging':
        table_sql = f"""
                    CREATE TABLE IF NOT EXISTS {schema}.{table} (
                        "Video_ID" VARCHAR(11) PRIMARY KEY NOT NULL,
                        "Video_Title" TEXT NOT NULL,
                        "Upload_Date" TIMESTAMP NOT NULL,
                        "Duration" VARCHAR(20) NOT NULL,
                        "Video_Views" INT,
                        "Likes_Count" INT,
                        "Comments_Count" INT   
                    );
                """
    else:
        table_sql = f"""
                  CREATE TABLE IF NOT EXISTS {schema}.{table} (
                      "Video_ID" VARCHAR(11) PRIMARY KEY NOT NULL,
                      "Video_Title" TEXT NOT NULL,
                      "Upload_Date" TIMESTAMP NOT NULL,
                      "Duration" TIME NOT NULL,
                      "Video_Type" VARCHAR(10) NOT NULL,
                      "Video_Views" INT,
                      "Likes_Count" INT,
                      "Comments_Count" INT    
                  ); 
              """        

    cur.execute(table_sql)

    conn.commit()
    closeConnCursor(conn, cur)


def getVideoIds(cur, schema):
    cur.execute(f"""SELECT "Video_ID" FROM {schema}.{table};""")
    ids = cur.fetchall()

    video_ids = [row["Video_ID"] for row in ids]

    return video_ids