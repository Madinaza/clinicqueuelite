from database import get_db

# ---------- Doctor mapping ----------
def get_or_link_doctor_for_user(user_id: int):
    """
    Return doctor row linked to this doctor user.
    If doctors.user_id column doesn't exist yet, we add it (safe).
    If no link exists, we auto-link the first doctor row to this user (demo-friendly).
    """
    db = get_db()

    # Ensure doctors.user_id exists (no init_db needed)
    try:
        db.execute("SELECT user_id FROM doctors LIMIT 1")
    except Exception:
        db.execute("ALTER TABLE doctors ADD COLUMN user_id INTEGER")
        db.commit()

    doctor = db.execute(
        "SELECT * FROM doctors WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    if doctor:
        return doctor

    # Demo-friendly auto-link:
    # link first doctor that has no user_id yet
    free_doc = db.execute(
        "SELECT * FROM doctors WHERE user_id IS NULL ORDER BY id ASC LIMIT 1"
    ).fetchone()

    if free_doc:
        db.execute("UPDATE doctors SET user_id=? WHERE id=?", (user_id, free_doc["id"]))
        db.commit()
        return db.execute("SELECT * FROM doctors WHERE id=?", (free_doc["id"],)).fetchone()

    return None


# ---------- Availability ----------
def update_doctor_status(doctor_id: int, status: str):
    db = get_db()
    db.execute("UPDATE doctors SET status=? WHERE id=?", (status, doctor_id))
    db.commit()


# ---------- Queue / Requests ----------
def get_counts(doctor_id: int):
    db = get_db()

    active_count = db.execute("""
        SELECT COUNT(*) AS c
        FROM appointments
        WHERE doctor_id=?
          AND status IN ('WAITING','ACCEPTED','IN_PROGRESS')
    """, (doctor_id,)).fetchone()["c"]

    waiting_count = db.execute("""
        SELECT COUNT(*) AS c
        FROM appointments
        WHERE doctor_id=? AND status='WAITING'
    """, (doctor_id,)).fetchone()["c"]

    return active_count, waiting_count


def get_doctor_requests(doctor_id: int):
    db = get_db()

    waiting = db.execute("""
        SELECT a.id, a.status, a.created_at, a.responded_at,
               u.email AS patient_email
        FROM appointments a
        JOIN users u ON u.id = a.patient_id
        WHERE a.doctor_id=? AND a.status='WAITING'
        ORDER BY a.created_at ASC
    """, (doctor_id,)).fetchall()

    active = db.execute("""
        SELECT a.id, a.status, a.created_at, a.responded_at,
               u.email AS patient_email
        FROM appointments a
        JOIN users u ON u.id = a.patient_id
        WHERE a.doctor_id=? AND a.status IN ('ACCEPTED','IN_PROGRESS')
        ORDER BY a.created_at ASC
    """, (doctor_id,)).fetchall()

    done = db.execute("""
        SELECT a.id, a.status, a.created_at, a.responded_at,
               u.email AS patient_email
        FROM appointments a
        JOIN users u ON u.id = a.patient_id
        WHERE a.doctor_id=? AND a.status IN ('DONE','REJECTED')
        ORDER BY a.id DESC
        LIMIT 12
    """, (doctor_id,)).fetchall()

    return waiting, active, done


def _set_status(appointment_id: int, status: str, touch_responded: bool = False):
    db = get_db()
    if touch_responded:
        db.execute("""
            UPDATE appointments
            SET status=?,
                responded_at=strftime('%s','now')
            WHERE id=?
        """, (status, appointment_id))
    else:
        db.execute("UPDATE appointments SET status=? WHERE id=?", (status, appointment_id))
    db.commit()


def accept_request(appointment_id: int):
    _set_status(appointment_id, "ACCEPTED", touch_responded=True)


def reject_request(appointment_id: int):
    _set_status(appointment_id, "REJECTED", touch_responded=True)


def start_request(appointment_id: int):
    _set_status(appointment_id, "IN_PROGRESS")


def complete_request(appointment_id: int):
    _set_status(appointment_id, "DONE")


def call_next(doctor_id: int):
    """
    Pick oldest WAITING and mark ACCEPTED.
    """
    db = get_db()
    row = db.execute("""
        SELECT id
        FROM appointments
        WHERE doctor_id=? AND status='WAITING'
        ORDER BY created_at ASC
        LIMIT 1
    """, (doctor_id,)).fetchone()

    if not row:
        return None

    accept_request(row["id"])
    return row["id"]
