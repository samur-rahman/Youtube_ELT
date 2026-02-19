from datawarehouse.data_utils import (
    getConnCursor,
    closeConnCursor,
    createSchema,
    createTable,
    getVideoIds,
)
from datawarehouse.data_loading import loadData
from datawarehouse.data_modification import insertRows, updateRows, deleteRows
from datawarehouse.data_transformation import transformData

import logging
from airflow.decorators import task

logger = logging.getLogger(__name__)
table = "yt_api"


@task
def stagingTable():
    schema = 'staging'
    conn, cur = None, None

    try:
        conn, cur = getConnCursor()

        YT_data = loadData()

        createSchema(schema)
        createTable(schema)

        table_ids = getVideoIds(cur, schema)

        for row in YT_data:
            if len(table_ids) == 0:
                insertRows(cur, conn, schema, row)

            else:
                if row['video_id'] in table_ids:
                    updateRows(cur, conn, schema, row)
                else:
                    insertRows(cur, conn, schema, row)

        ids_in_json = {row['video_id'] for row in YT_data}
        ids_to_delete = set(table_ids) - ids_in_json

        if ids_to_delete:
            deleteRows(cur, conn, schema, ids_to_delete)

        logger.info(f"{schema} table update complete")

    except Exception as e:
        logger.error(f"An error occurred during the update of {schema} table: {e}")
        raise e

    finally:
        if conn and cur:
            closeConnCursor(conn, cur)


@task
def coreTable():
    schema = "core"
    conn, cur = None, None

    try:
        conn, cur = getConnCursor()

        createSchema(schema)
        createTable(schema)
        
        table_ids = getVideoIds(cur, schema)

        current_video_ids = set()

        cur.execute(f"SELECT * FROM staging.{table};")
        rows = cur.fetchall()

        for row in rows:
            current_video_ids.add(row["Video_ID"])

            if len(table_ids) == 0:
                transformed_row = transformData(row)
                insertRows(cur, conn, schema, transformed_row)
            else:
                transformed_row = transformData(row)

                if transformed_row["Video_ID"] in table_ids:
                    updateRows(cur, conn, schema, transformed_row)

                else:
                    insertRows(cur, conn, schema, transformed_row)

        ids_to_delete = set(table_ids) - current_video_ids

        if ids_to_delete:
            deleteRows(cur, conn, schema, ids_to_delete)

        logger.info(f"{schema} table update completed")

    except Exception as e:
        # Log any exceptions that occur
        logger.error(f"An error occurred during the update of {schema} table: {e}")
        raise e

    finally:
        # Ensure the connection and cursor are closed
        if conn and cur:
            closeConnCursor(conn, cur)