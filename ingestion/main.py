import os
import time
import pandas as pd
from dotenv import load_dotenv
from fetcher import fetch_recent_events
from staging import insert_df, ensure_table, wait_for_db
from schema import schemas

load_dotenv()

# Environment variables
table_name = "earthquake_minute"
poll_interval = int(os.getenv("POLL_INTERVAL", 15))  # seconds
fetch_window = int(os.getenv("FETCH_WINDOW_MINUTES", 1))  # minutes

def main():
    print(f"Environment loaded. Connecting to DB: {os.getenv('MYSQL_HOST')}")
    wait_for_db()
    ensure_table(table_name, schemas.get(table_name))

    while True:
        try:
            events = fetch_recent_events(minutes=fetch_window)
            if events:
                df = pd.DataFrame([e.__dict__ for e in events])
                insert_df(df, table_name)
            else:
                print("No earthquakes detected in the last period.")
        except Exception as e:
            print("Error during fetch/stage:", e)
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
