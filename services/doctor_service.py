from database import get_db


# -----------------------------
# Doctor identification
# -----------------------------
def get_current_doctor_id_from_session(session):
    """
    If you use temp doctor login (doctors table has email/password),
    you store session['doctor_id'] at login.
    """
    return session.get("doctor_id")


def get_doctor(doctor_id: int):
    db = get_db()
    return db.execute("SELECT * FROM doctors WHERE id=?", (doctor_id,)).fetchone()


# -----------------------------
# Doctor status
# -----------------------------
def update_doctor_status(doctor_id: int, status: str):
    db = get_db()
    db.execute("UPDATE doctors SET status=? WHERE id=?", (status, doctor_id))
    db.commit()


# -----------------------------
# Requests lists
# -----------------------------
def get_doctor_requests(doctor_id: int):
    db = get_db()

    waiting = db.execute(
        """
        SELECT a.id, a.status, a.created_at, a.responded_at, a.note,
               u.email AS patient_email
        FROM appointments a
        JOIN users u ON u.id = a.patient_id
        WHERE a.doctor_id = ?
          AND a.status = 'WAITING'
        ORDER BY a.id DESC
        """,
        (doctor_id,),
    ).fetchall()

    active = db.execute(
        """
        SELECT a.id, a.status, a.created_at, a.responded_at, a.note,
               u.email AS patient_email
        FROM appointments a
        JOIN users u ON u.id = a.patient_id
        WHERE a.doctor_id = ?
          AND a.status IN ('ACCEPTED','IN_PROGRESS')
        ORDER BY a.id DESC
        """,
        (doctor_id,),
    ).fetchall()

    done = db.execute(
        """
        SELECT a.id, a.status, a.created_at, a.responded_at, a.completed_at, a.note,
               u.email AS patient_email
        FROM appointments a
        JOIN users u ON u.id = a.patient_id
        WHERE a.doctor_id = ?
          AND a.status IN ('DONE','REJECTED')
        ORDER BY a.id DESC
        LIMIT 20
        """,
        (doctor_id,),
    ).fetchall()

    return waiting, active, done


def get_counts(doctor_id: int):
    db = get_db()
    active_count = db.execute(
        """
        SELECT COUNT(*) AS c
        FROM appointments
        WHERE doctor_id = ?
          AND status IN ('ACCEPTED','IN_PROGRESS')
        """,
        (doctor_id,),
    ).fetchone()["c"]

    waiting_count = db.execute(
        """
        SELECT COUNT(*) AS c
        FROM appointments
        WHERE doctor_id = ?
          AND status = 'WAITING'
        """,
        (doctor_id,),
    ).fetchone()["c"]

    return active_count, waiting_count


# -----------------------------
# Transitions (safe)
# -----------------------------
def accept_request(appointment_id: int, doctor_id: int):
    db = get_db()
    db.execute(
        """
        UPDATE appointments
        SET status='ACCEPTED', responded_at=strftime('%s','now')
        WHERE id=? AND doctor_id=? AND status='WAITING'
        """,
        (appointment_id, doctor_id),
    )
    db.commit()


def reject_request(appointment_id: int, doctor_id: int):
    db = get_db()
    db.execute(
        """
        UPDATE appointments
        SET status='REJECTED', responded_at=strftime('%s','now')
        WHERE id=? AND doctor_id=? AND status='WAITING'
        """,
        (appointment_id, doctor_id),
    )
    db.commit()


def start_request(appointment_id: int, doctor_id: int):
    db = get_db()
    db.execute(
        """
        UPDATE appointments
        SET status='IN_PROGRESS'
        WHERE id=? AND doctor_id=? AND status='ACCEPTED'
        """,
        (appointment_id, doctor_id),
    )
    db.commit()


def complete_request(appointment_id: int, doctor_id: int):
    db = get_db()
    db.execute(
        """
        UPDATE appointments
        SET status='DONE', completed_at=strftime('%s','now')
        WHERE id=? AND doctor_id=? AND status='IN_PROGRESS'
        """,
        (appointment_id, doctor_id),
    )
    db.commit()


def call_next(doctor_id: int):
    """
    Picks the oldest WAITING request and accepts it.
    """
    db = get_db()
    row = db.execute(
        """
        SELECT id FROM appointments
        WHERE doctor_id=? AND status='WAITING'
        ORDER BY id ASC
        LIMIT 1
        """,
        (doctor_id,),
    ).fetchone()

    if not row:
        return False

    db.execute(
        """
        UPDATE appointments
        SET status='ACCEPTED', responded_at=strftime('%s','now')
        WHERE id=? AND doctor_id=?
        """,
        (row["id"], doctor_id),
    )
    db.commit()
    return True


def update_note(appointment_id: int, doctor_id: int, note: str):
    db = get_db()
    db.execute(
        """
        UPDATE appointments
        SET note=?
        WHERE id=? AND doctor_id=?
        """,
        (note, appointment_id, doctor_id),
    )
    db.commit()


# ------------------------------------------
# Compatibility: keep your old import working
# ------------------------------------------
def get_or_link_doctor_for_user(user_id: int):
    """
    OLD NAME (compatibility).
    For temp doctor login, user_id == doctors.id.
    """
    db = get_db()
    return db.execute("SELECT * FROM doctors WHERE id=?", (user_id,)).fetchone()
