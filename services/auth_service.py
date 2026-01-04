from database import get_db


def authenticate(email, password):
    email = (email or "").strip().lower()
    password = password or ""

    db = get_db()

    # 1) USERS table (patients + admin + optional doctor users)
    user = db.execute(
        "SELECT id, email, role FROM users WHERE lower(email)=? AND password=?",
        (email, password)
    ).fetchone()

    if user:
        doctor_id = None
        if user["role"] == "doctor":
            row = db.execute("SELECT id FROM doctors WHERE user_id=?", (user["id"],)).fetchone()
            doctor_id = row["id"] if row else None
        return {"id": user["id"], "email": user["email"], "role": user["role"], "doctor_id": doctor_id}

    # 2) DOCTORS temp login
    doctor = db.execute(
        "SELECT id, email FROM doctors WHERE lower(email)=? AND password=?",
        (email, password)
    ).fetchone()

    if doctor:
        # create a virtual "user_id" session for doctor panel
        return {"id": doctor["id"], "email": doctor["email"], "role": "doctor", "doctor_id": doctor["id"]}

    return None


def email_exists(email):
    email = (email or "").strip().lower()
    row = get_db().execute("SELECT 1 FROM users WHERE lower(email)=?", (email,)).fetchone()
    return row is not None


def register_patient(email, password):
    try:
        db = get_db()
        db.execute(
            "INSERT INTO users (email,password,role) VALUES (?,?, 'patient')",
            ((email or "").strip().lower(), password)
        )
        db.commit()
        return True
    except:
        return False


def update_password(email, new_password):
    db = get_db()
    db.execute("UPDATE users SET password=? WHERE lower(email)=?", (new_password, (email or "").strip().lower()))
    db.commit()
    return True