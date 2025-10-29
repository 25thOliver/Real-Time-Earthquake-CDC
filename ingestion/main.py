import pandas as pd
from ingestion.fetcher import fetch_last_minute_events
from ingestion.staging import insert_df, ensure_table, wait_for_db
from dotenv import load_dotenv
import time
import os

load_dotenv()

table_name = "earthquake_minutes"
poll_interval = int(os.getenv("POLL_INTERVAL", 15))

def main():
    wait_for_db()
    ensure_table(table_name)

    while True:
        try:
            events = fetch_last_minute_events()
            if events:
                df = pd.DataFrame([e.__dict__ for e in events])
                insert_df(df, table_name)
            else:
                print("No earthquakes detected in the last minute.")
        except Exception as e:
            print("Error during fetch/stage:", e)
        time.sleep(poll_interval)