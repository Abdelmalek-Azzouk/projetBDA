import sys
import os
import sqlite3

def generate_accounts_db():
    print("Initializing Accounts Database...")
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    db_path = os.path.join(data_dir, "accounts.db")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    tables = [
        ("doyen", "doyen", "doyenpw"),
        ("chef", "chef", "chefpw"),
        ("student", "student", "studentpw"),
        ("teacher", "teacher", "teacherpw"),
        ("examgestionnaire", "gest", "gestpw"),
    ]

    for role, uname, pw in tables:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {role} (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        # Insert only if not present
        cur.execute(f"SELECT COUNT(*) FROM {role} WHERE username=?", (uname,))
        if cur.fetchone()[0] == 0:
            cur.execute(f"INSERT INTO {role} (username, password) VALUES (?, ?)", (uname, pw))

    conn.commit()
    conn.close()
    print("Accounts DB generation complete!")

if __name__ == "__main__":
    generate_accounts_db()
