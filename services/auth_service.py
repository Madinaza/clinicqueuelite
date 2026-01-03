from database import get_db


def authenticate(email, password):
    email = (email or "").strip().lower()
    password = password or ""

    db = get_db()

    # 1) USERS table (patient + ADMIN)
    user = db.execute(
        "SELECT id, email, role FROM users WHERE lower(email)=? AND password=?",
        (email, password),
    ).fetchone()

    if user:
        return {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "doctor_id": None,
        }

    # 2) DOCTORS table (temporary doctor login)
    doctor = db.execute(
        "SELECT id, email FROM doctors WHERE lower(email)=? AND password=?",
        (email, password),
    ).fetchone()

    if doctor:
        return {
            "id": doctor["id"],
            "email": doctor["email"],
            "role": "doctor",
            "doctor_id": doctor["id"],
        }

    return None


def email_exists(email):
    email = (email or "").strip().lower()
    db = get_db()
    row = db.execute(
        "SELECT 1 FROM users WHERE lower(email)=?",
        (email,),
    ).fetchone()
    return row is not None


def register_patient(email, password):
    email = (email or "").strip().lower()
    password = password or ""

    try:
        db = get_db()
        db.execute(
            "INSERT INTO users (email,password,role) VALUES (?,?, 'patient')",
            (email, password),
        )
        db.commit()
        return True
    except:
        return False


def update_password(email, new_password):
    email = (email or "").strip().lower()
    new_password = new_password or ""

    db = get_db()
    db.execute(
        "UPDATE users SET password=? WHERE lower(email)=?",
        (new_password, email),
    )
    db.commit()
    return True
