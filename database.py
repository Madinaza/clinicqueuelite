import sqlite3
from flask import g

DB_PATH = "clinicflow.db"


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db = conn
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def ensure_db():
    """
    Runs outside request context.
    - Creates tables (schema.sql)
    - Adds missing columns (migrations)
    - Seeds demo admin + doctors
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    def has_column(table: str, col: str) -> bool:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        return any(r["name"] == col for r in rows)

    # ---- migrations (safe for old DBs) ----
        # ---- migrations for old DBs ----
    if not has_column("doctors", "user_id"):
        conn.execute("ALTER TABLE doctors ADD COLUMN user_id INTEGER UNIQUE")

    if not has_column("doctors", "email"):
        conn.execute("ALTER TABLE doctors ADD COLUMN email TEXT UNIQUE")

    if not has_column("doctors", "password"):
        conn.execute("ALTER TABLE doctors ADD COLUMN password TEXT")

    if not has_column("appointments", "note"):
        conn.execute("ALTER TABLE appointments ADD COLUMN note TEXT")

    if not has_column("appointments", "completed_at"):
        conn.execute("ALTER TABLE appointments ADD COLUMN completed_at INTEGER")

    # ✅ booking date/time migrations
    if not has_column("appointments", "appt_date"):
        conn.execute("ALTER TABLE appointments ADD COLUMN appt_date TEXT")

    if not has_column("appointments", "appt_time"):
        conn.execute("ALTER TABLE appointments ADD COLUMN appt_time TEXT")

    # ---- seed demo admin ----
    conn.execute("""
        INSERT OR IGNORE INTO users (email,password,role)
        VALUES ('admin@clinicflow.local','admin1234','ADMIN')
    """)

    # ---- seed doctors with temp login ----
    conn.execute("""
        INSERT OR IGNORE INTO doctors (id,name,branch,experience,address,status,email,password)
        VALUES
          (1,'Dr. Ahmed Hassan','Cardiology',12,'Main Clinic - Floor 2','AVAILABLE','ahmed@clinicflow.local','doctor123'),
          (2,'Dr. Sarah Ali','Dermatology',8,'West Wing - Room 14','AVAILABLE','sarah@clinicflow.local','doctor123'),
          (3,'Dr. John Smith','Neurology',15,'East Wing - Room 9','BUSY','john@clinicflow.local','doctor123')
    """)

    conn.commit()
    conn.close()