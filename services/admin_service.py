from database import get_db


def get_admin_stats():
    db = get_db()

    users = db.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    doctors = db.execute("SELECT COUNT(*) AS c FROM doctors").fetchone()["c"]

    waiting = db.execute("""
        SELECT COUNT(*) AS c
        FROM appointments
        WHERE status='WAITING'
    """).fetchone()["c"]

    active = db.execute("""
        SELECT COUNT(*) AS c
        FROM appointments
        WHERE status IN ('ACCEPTED','IN_PROGRESS')
    """).fetchone()["c"]

    done_today = db.execute("""
        SELECT COUNT(*) AS c
        FROM appointments
        WHERE status='DONE'
          AND date(datetime(responded_at, 'unixepoch')) = date('now')
    """).fetchone()["c"]

    return {
        "users": users,
        "doctors": doctors,
        "waiting": waiting,
        "active": active,
        "done_today": done_today
    }


def list_doctors():
    db = get_db()
    return db.execute("""
        SELECT id, name, branch, experience, address, status
        FROM doctors
        ORDER BY id DESC
    """).fetchall()


def add_doctor(name, branch, experience, address, status="AVAILABLE"):
    db = get_db()
    db.execute("""
        INSERT INTO doctors (name, branch, experience, address, status)
        VALUES (?, ?, ?, ?, ?)
    """, (name, branch, experience, address, status))
    db.commit()


def update_doctor_status(doctor_id, status):
    db = get_db()
    db.execute("UPDATE doctors SET status=? WHERE id=?", (status, doctor_id))
    db.commit()


def delete_doctor(doctor_id):
    db = get_db()
    # optional safety: remove related appointments first
    db.execute("DELETE FROM appointments WHERE doctor_id=?", (doctor_id,))
    db.execute("DELETE FROM doctors WHERE id=?", (doctor_id,))
    db.commit()


def list_appointments(limit=200):
    db = get_db()
    return db.execute(f"""
        SELECT
            a.id,
            a.status,
            a.created_at,
            a.responded_at,
            u.email AS patient_email,
            d.name AS doctor_name,
            d.branch
        FROM appointments a
        JOIN users u ON u.id = a.patient_id
        JOIN doctors d ON d.id = a.doctor_id
        ORDER BY a.id DESC
        LIMIT {int(limit)}
    """).fetchall()


def admin_set_appointment_status(appointment_id, status):
    db = get_db()

    # set responded_at only when leaving WAITING
    if status in ("ACCEPTED", "REJECTED", "IN_PROGRESS", "DONE", "CANCELLED"):
        db.execute("""
            UPDATE appointments
            SET status=?,
                responded_at = COALESCE(responded_at, strftime('%s','now'))
            WHERE id=?
        """, (status, appointment_id))
        db.commit()
