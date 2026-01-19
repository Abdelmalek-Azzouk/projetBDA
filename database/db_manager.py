import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'university.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def init_db():
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Schema file not found at {SCHEMA_PATH}")

    conn = get_connection()
    try:
        with open(SCHEMA_PATH, 'r') as f:
            conn.executescript(f.read())
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing DB: {e}")
    finally:
        conn.close()

def run_query(query, params=()):
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn, params=params)
        return df
    except Exception as e:
        print(f"Query Error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def execute_statement(statement, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(statement, params)
        conn.commit()
        rows_affected = cursor.rowcount
        return rows_affected
    except Exception as e:
        print(f"Execution Error: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()
        
def set_edt_validation(is_validated: bool):
    """Sets the validation status (1 = Published, 0 = Draft)"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)")
    
    val = "1" if is_validated else "0"
    cur.execute("INSERT OR REPLACE INTO system_config (key, value) VALUES ('edt_published', ?)", (val,))
    conn.commit()
    conn.close()

def is_edt_validated():
    """Returns True if EDT is published, False otherwise"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS system_config (key TEXT PRIMARY KEY, value TEXT)")
    
    cur.execute("SELECT value FROM system_config WHERE key='edt_published'")
    row = cur.fetchone()
    conn.close()
    
    if row and row[0] == "1":
        return True
    return False