import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # directory of this script
DB_PATH = BASE_DIR / "budgeting.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def db_init(schema: str):
    "Initializes the DB according to the SQL schema"
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        if not tables:
            with open(schema, 'r') as sql_file:
                sql_schema = sql_file.read()
            
            db.executescript(sql_schema)
            db.commit()


def get_purchases(as_df: bool = True):
    query = 'SELECT * FROM Purchase'
    
    with sqlite3.connect(DB_PATH) as db:
        if as_df:
            df = pd.read_sql(query, db)
            return df
        else:
            rows = db.execute(query)
            return rows

