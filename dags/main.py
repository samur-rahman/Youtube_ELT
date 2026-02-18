from airflow import DAG
import pendulum
from datetime import datetime, timedelta
from api.video_stats import getPlaylistID, getVideoIDs, extractVideoData, saveToJson

#define local timezone
local_tz = pendulum.timezone('America/New_York')

# default args
defalut_args = {
    "owner": "samurrahman",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "rahman.ahotasamur@gmail.com",
    # "retries": 1,
    # "retry_delay": timedelta(minutes=5),
    "max_active_runs": 1,
    "dagrun_timeout": timedelta(hours=1),
    "start_date": datetime(2026, 1, 1, tzinfo=local_tz),
    # "end_date": datetime(2030, 12, 31, tzinfo=local_tz),
}


with DAG(
    dag_id='produce_json',
    default_args=defalut_args,
    description="DAG to produce JSON file with raw data",
    schedule='0 14 * * *',
    catchup=False
) as dag:
    
    # Define tasks
    playlist_id = getPlaylistID()
    video_ids = getVideoIDs(playlist_id)
    extract_data = extractVideoData(video_ids)
    save_to_json = saveToJson(extract_data)

    # Define Dependencies
    playlist_id >> video_ids >> extract_data >> save_to_json