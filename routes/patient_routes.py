from flask import Blueprint, render_template, redirect, session, request
from database import get_db

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")


def _require_patient():
    return session.get("user_id") and session.get("role") == "patient"


@patient_bp.route("/dashboard")
def dashboard():
    if not _require_patient():
        return redirect("/login?next=/patient/dashboard")

    db = get_db()
    rows = db.execute("""
        SELECT
            a.id, a.status, a.created_at, a.responded_at, a.completed_at,
            a.appt_date, a.appt_time, a.note,
            d.name AS doctor_name, d.branch, d.address
        FROM appointments a
        JOIN doctors d ON d.id = a.doctor_id
        WHERE a.patient_id = ?
        ORDER BY a.id DESC
    """, (session["user_id"],)).fetchall()

    return render_template("patient_panel.html", appointments=rows)


@patient_bp.route("/request/<int:doctor_id>", methods=["POST"])
def request_appointment(doctor_id):
    if not _require_patient():
        return redirect(f"/login?next=/")

    appt_date = request.form.get("appt_date")
    appt_time = request.form.get("appt_time")

    if not appt_date or not appt_time:
        return redirect("/?error=pick_datetime")

    db = get_db()

    doc = db.execute("SELECT status FROM doctors WHERE id=?", (doctor_id,)).fetchone()
    if not doc or doc["status"] != "AVAILABLE":
        return redirect("/?error=not_available")

    # prevent duplicate slot
    slot_taken = db.execute("""
        SELECT 1 FROM appointments
        WHERE doctor_id=? AND appt_date=? AND appt_time=?
          AND status IN ('WAITING','ACCEPTED','IN_PROGRESS')
    """, (doctor_id, appt_date, appt_time)).fetchone()

    if slot_taken:
        return redirect("/?error=slot_taken")

    # prevent spam: one WAITING per doctor per patient
    already_waiting = db.execute("""
        SELECT 1 FROM appointments
        WHERE patient_id=? AND doctor_id=? AND status='WAITING'
    """, (session["user_id"], doctor_id)).fetchone()

    if already_waiting:
        return redirect("/patient/dashboard")

    db.execute("""
        INSERT INTO appointments (patient_id, doctor_id, status, created_at, appt_date, appt_time)
        VALUES (?, ?, 'WAITING', strftime('%s','now'), ?, ?)
    """, (session["user_id"], doctor_id, appt_date, appt_time))
    db.commit()

    return redirect("/patient/dashboard")


@patient_bp.route("/cancel/<int:appointment_id>")
def cancel(appointment_id):
    if not _require_patient():
        return redirect("/login?next=/patient/dashboard")

    db = get_db()
    db.execute("""
        UPDATE appointments
        SET status='CANCELLED',
            completed_at=strftime('%s','now')
        WHERE id=? AND patient_id=? AND status IN ('WAITING','ACCEPTED')
    """, (appointment_id, session["user_id"]))
    db.commit()

    return redirect("/patient/dashboard")