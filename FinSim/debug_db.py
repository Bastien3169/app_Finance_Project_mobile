import sqlite3
from datetime import datetime, timezone

DB = "users.db"

def dump_users():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT id, username, email, role, registration_date FROM users")
        rows = c.fetchall()
        print("===== USERS =====")
        for r in rows:
            print(r)

def dump_sessions():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT session_id, user_id, expires_at FROM sessions")
        rows = c.fetchall()
        print("===== SESSIONS =====")
        for r in rows:
            print(r)

if __name__ == "__main__":
    dump_users()
    dump_sessions()
    print("Now (UTC):", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
