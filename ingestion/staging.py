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


def ensure_table(table_name: str, schema_sql: str | None = None):
    ddl = schema_sql or schemas.get(table_name)
    if ddl:
        with engine.begin() as conn:
            conn.execute(text(ddl))
        print(f"Table '{table_name}' verified/created.")


def insert_df(df: pd.DataFrame, table_name: str):
    if df.empty:
        print("No new rows to insert.")
        return

    try:
        with engine.begin() as conn:
            temp_table = f"_{table_name}_temp"
            df.to_sql(temp_table, conn, if_exists="replace", index=False)

            cols = list(df.columns)
            cols_str = ", ".join(cols)
            update_assignments = ", ".join([f"`{col}` = VALUES(`{col}`)" for col in cols if col != "id"])

            upsert_query = f"""
                INSERT INTO {table_name} ({cols_str})
                SELECT {cols_str} FROM {temp_table}
                ON DUPLICATE KEY UPDATE {update_assignments};
            """

            conn.execute(text(upsert_query))
            conn.execute(text(f"DROP TABLE `{temp_table}`;"))
        print(f"Successfully staged {len(df)} records into '{table_name}' (UPSERT executed).")
    except Exception as e:
        print(f"Error upserting data into database: {e}")


def get_max_updated_at(table_name: str) -> int | None:
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT MAX(updated_ms) FROM {table_name}"))
            val = result.scalar()
            return int(val) if val is not None else None
    except Exception as e:
        print(f"Could not retrieve max updated timestamp: {e}")
        return None