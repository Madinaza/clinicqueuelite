from database import get_db

def insert_patient(name, urgency, checkin_ts):
    db = get_db()
    db.execute(
        """
        INSERT INTO patients (name, urgency, checkin_ts, status)
        VALUES (?, ?, ?, 'WAITING')
        """,
        (name, urgency, checkin_ts),
    )
    db.commit()


def get_waiting_patients():
    db = get_db()
    return db.execute(
        "SELECT * FROM patients WHERE status='WAITING' ORDER BY urgency DESC, checkin_ts ASC"
    ).fetchall()


def update_urgency(pid, urgency):
    db = get_db()
    db.execute("UPDATE patients SET urgency=? WHERE id=?", (urgency, pid))
    db.commit()


def complete_patient(pid):
    db = get_db()
    db.execute("UPDATE patients SET status='DONE' WHERE id=?", (pid,))
    db.commit()


def delete_patient(pid):
    db = get_db()
    db.execute("DELETE FROM patients WHERE id=?", (pid,))
    db.commit()
