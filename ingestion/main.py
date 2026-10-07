import os
import time
import pandas as pd
from dotenv import load_dotenv
from ingestion.fetcher import fetch_events_updated_after
from ingestion.staging import insert_df, ensure_table, wait_for_db, get_max_updated_at
from ingestion.schema import schemas
from datetime import datetime, timedelta, timezone

load_dotenv()

table_name = "earthquake_minute"
poll_interval = int(os.getenv("POLL_INTERVAL", 60))
default_lookback_minutes = int(os.getenv("INITIAL_LOOKBACK_MINUTES", 60))


def main():
    print(f"Environment loaded. Connecting to DB: {os.getenv('MYSQL_HOST')}")
    wait_for_db()
    ensure_table(table_name, schemas.get(table_name))

    while True:
        try:
            max_updated_ms = get_max_updated_at(table_name)
            if max_updated_ms:
                watermark = datetime.fromtimestamp(max_updated_ms / 1000.0, tz=timezone.utc) - timedelta(minutes=1)
            else:
                watermark = datetime.now(timezone.utc) - timedelta(minutes=default_lookback_minutes)

            print(f"[{datetime.now(timezone.utc).isoformat()}] Polling USGS API for events updated after {watermark.isoformat()}...")
            events = fetch_events_updated_after(watermark)

            if events:
                df = pd.DataFrame([e.__dict__ for e in events])
                insert_df(df, table_name)
            else:
                print("No new or updated earthquakes detected in this poll cycle.")
        except Exception as e:
            print("Error during fetch/stage cycle:", e)
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()