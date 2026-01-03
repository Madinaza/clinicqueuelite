import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "clinicflow.db")

def has_column(db, table, col):
    rows = db.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)

def main():
    db = sqlite3.connect(DB_PATH)

    # appointments columns
    if not has_column(db, "appointments", "started_at"):
        db.execute("ALTER TABLE appointments ADD COLUMN started_at INTEGER")

    if not has_column(db, "appointments", "completed_at"):
        db.execute("ALTER TABLE appointments ADD COLUMN completed_at INTEGER")

    if not has_column(db, "appointments", "doctor_note"):
        db.execute("ALTER TABLE appointments ADD COLUMN doctor_note TEXT")

    # doctors mapping
    if not has_column(db, "doctors", "user_id"):
        db.execute("ALTER TABLE doctors ADD COLUMN user_id INTEGER")

    db.commit()
    db.close()
    print("✅ Migration done successfully")

if __name__ == "__main__":
    main()
