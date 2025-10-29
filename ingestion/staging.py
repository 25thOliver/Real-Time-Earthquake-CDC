import os
import time
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
from ingestion.schema import schemas

load_dotenv()

db_user = os.getenv("MYSQL_USER")
db_pass = os.getenv("MYSQL_PASSWORD")
db_name = os.getenv("MYSQL_DATABASE")
db_host = os.getenv("MYSQL_HOST", "mysql")
db_port = os.getenv("MYSQL_PORT", 3306)

db_url = f"mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
engine = create_engine(db_url, pool_pre_ping=True)

# wait until DB is reachable for staging
def wait_for_db(max_retries=10, delay=5):
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection established!")
            return
        except OperationalError:
            print(f"Waiting for database... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
    raise Exception("Could not connect to database after several attempts.")


# Ensure table exists according to defined schema
def ensure_table(table_name: str):
    ddl = schemas.get(table_name)
    if ddl:
        with engine.begin() as conn:
            conn.execute(text(ddl))
        print("Table '{table_name}' verified/created.")
    else:
        print(f"No schema found for table '{table_name}', skipping explicit creation.")


# Insert DataFrame to MySQL, letting pandas create table if not exists
def insert_df(df: pd.DataFrame, table_name: str):
    if df.empty:
        print("No new rows to insert.")
        return
    df.to_sql(table_name, engine, if_exists="append", index=False)
    print(f"Inserted {len(df)} rows into '{table_name}'.")
