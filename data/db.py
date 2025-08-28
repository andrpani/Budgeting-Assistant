import sqlite3
import os
import pandas as pd
from pathlib import Path
from data.models import Purchase
from typing import List

#BASE_DIR = Path(__file__).resolve().parent  # directory of this script
DB_PATH = Path(__file__).parent / "budgeting.db"
#SCHEMA_PATH = BASE_DIR / "schema.sql" 

INIT_QUERY = """
    CREATE TABLE "Purchase" (
    "ID"	    INTEGER NOT NULL UNIQUE,
	"Title"	    TEXT,
	"Date"	    TEXT,
	"Total"	    REAL,
	PRIMARY KEY("ID" AUTOINCREMENT)
);

    CREATE TABLE "PurchaseItem" (
        "ID"        INTEGER NOT NULL UNIQUE,
        "Name"      TEXT,
        "Quantity"  INTEGER,
        "UnitPrice" REAL,
        "TotPrice"  REAL,
        "Info"      TEXT,
        "PurchaseID"  INTEGER NOT NULL,
        FOREIGN KEY("PurchaseID") REFERENCES "Purchase" ("ID")
            ON UPDATE SET NULL ON DELETE SET NULL,
        PRIMARY KEY("ID" AUTOINCREMENT)
    );
"""

class BudgetingDBSQLite:
    def __init__(self):
        self.connection = None
        self.cursor = None
        if not Path(DB_PATH).exists():
            with sqlite3.connect(DB_PATH) as db:
                db.executescript(INIT_QUERY)
                db.commit()
    
    def __enter__(self):
        self.connection = sqlite3.connect('budgeting.db')
        self.cursor = self.connection.cursor()
    
    def __exit__(self):
        if self.connection:
            self.connection.close()

    
    def insert_purchases(self, purchases: List[Purchase]):
        with sqlite3.connect(DB_PATH) as db:
            cursor = db.cursor()
            for purchase in purchases:
                purchase_dict = purchase.model_dump()
                del purchase_dict['items']
                cursor.execute("INSERT INTO Purchase(Title, Date, Total) " \
                                            "VALUES (:title, :date, :total)", purchase_dict)
                db.commit()
                purchase_id = cursor.lastrowid
                for item in purchase.items:
                    item_dict = item.model_dump()
                    item_dict['purchase_id'] = purchase_id
                    cursor.execute("INSERT INTO PurchaseItem(Name, Quantity, UnitPrice, TotPrice, Info, PurchaseID)" \
                                        "VALUES (:name, :quantity, :unit_price, :tot_price, :info, :purchase_id)", item_dict)
                    db.commit()
    
    def get_purchases(self) -> List[dict]:
        with sqlite3.connect(DB_PATH) as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            cursor.execute('SELECT * FROM Purchase')
            purchases = []
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_purchase_items(self, purchases: List[dict]):
        with sqlite3.connect(DB_PATH) as db:
            db.row_factory = sqlite3.Row
            cursor = db.cursor()
            purchase_items = []
            for purchase in purchases:
                cursor.execute('SELECT * FROM PurchaseItem WHERE PurchaseID = ?', (purchase['ID'],))
                rows = cursor.fetchall()
                for row in rows:
                    purchase_items.append(dict(row))
            return purchase_items


"""     
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
"""

if __name__ == '__main__':
    get_purchases()