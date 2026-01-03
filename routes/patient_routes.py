from flask import Blueprint, render_template, redirect, session
from database import get_db

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")


def _require_patient():
    return session.get("role") == "patient" and session.get("user_id")


@patient_bp.route("/dashboard")
def dashboard():
    if not _require_patient():
        return redirect("/login")

    db = get_db()
    rows = db.execute("""
        SELECT
            a.id,
            a.status,
            d.name AS doctor_name
        FROM appointments a
        JOIN doctors d ON d.id = a.doctor_id
        WHERE a.patient_id = ?
        ORDER BY a.id DESC
    """, (session["user_id"],)).fetchall()

    return render_template("patient_panel.html", appointments=rows)


@patient_bp.route("/request/<int:doctor_id>")
def request_appointment(doctor_id):
    if not _require_patient():
        return redirect(f"/login?next=/patient/request/{doctor_id}")

    db = get_db()

    # if doctor offline -> block request
    doc = db.execute("SELECT status FROM doctors WHERE id=?", (doctor_id,)).fetchone()
    if not doc or doc["status"] == "OFFLINE":
        return redirect("/")

    # create WAITING appointment
    db.execute("""
        INSERT INTO appointments (patient_id, doctor_id, status, created_at)
        VALUES (?, ?, 'WAITING', strftime('%s','now'))
    """, (session["user_id"], doctor_id))
    db.commit()

    return redirect("/patient/dashboard")


@patient_bp.route("/cancel/<int:appointment_id>")
def cancel(appointment_id):
    if not _require_patient():
        return redirect("/login")

    db = get_db()
    db.execute("""
        UPDATE appointments
        SET status='CANCELLED'
        WHERE id=? AND patient_id=? AND status='WAITING'
    """, (appointment_id, session["user_id"]))
    db.commit()

    return redirect("/patient/dashboard")
