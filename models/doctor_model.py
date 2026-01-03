from database import get_db

def get_doctors():
    return get_db().execute(
        "SELECT * FROM doctors"
    ).fetchall()

def set_doctor_status(doc_id, status):
    db = get_db()
    db.execute(
        "UPDATE doctors SET status=? WHERE id=?",
        (status, doc_id)
    )
    db.commit()
