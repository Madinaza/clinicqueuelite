from flask import Blueprint, render_template, redirect, session, request
from database import get_db

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _require_admin():
    return session.get("user_id") and session.get("role") == "ADMIN"


@admin_bp.route("/dashboard")
def dashboard():
    if not _require_admin():
        return redirect("/login?next=/admin/dashboard")

    db = get_db()

    doctors = db.execute("""
        SELECT id,name,branch,experience,address,status,email
        FROM doctors
        ORDER BY id ASC
    """).fetchall()

    appointments = db.execute("""
        SELECT
          a.id, a.status, a.appt_date, a.appt_time, a.note,
          u.email AS patient_email,
          d.name AS doctor_name, d.branch
        FROM appointments a
        JOIN users u ON u.id = a.patient_id
        JOIN doctors d ON d.id = a.doctor_id
        ORDER BY a.id DESC
        LIMIT 40
    """).fetchall()

    return render_template("admin_panel.html", doctors=doctors, appointments=appointments)


@admin_bp.route("/doctor/status/<int:doctor_id>", methods=["POST"])
def doctor_status(doctor_id):
    if not _require_admin():
        return redirect("/login?next=/admin/dashboard")

    status = request.form.get("status", "AVAILABLE")
    if status not in ("AVAILABLE", "BUSY", "OFFLINE"):
        status = "AVAILABLE"

    db = get_db()
    db.execute("UPDATE doctors SET status=? WHERE id=?", (status, doctor_id))
    db.commit()

    return redirect("/admin/dashboard")


@admin_bp.route("/doctor/create", methods=["POST"])
def create_doctor():
    if not _require_admin():
        return redirect("/login?next=/admin/dashboard")

    name = request.form.get("name", "").strip()
    branch = request.form.get("branch", "").strip()
    experience = request.form.get("experience", "0").strip()
    address = request.form.get("address", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()

    if not (name and branch and address and email and password):
        return redirect("/admin/dashboard")

    try:
        exp = int(experience)
    except:
        exp = 0

    db = get_db()
    db.execute("""
        INSERT INTO doctors (name,branch,experience,address,status,email,password)
        VALUES (?,?,?,?, 'AVAILABLE', ?,?)
    """, (name, branch, exp, address, email, password))
    db.commit()

    return redirect("/admin/dashboard")


@admin_bp.route("/appointment/cancel/<int:appointment_id>")
def cancel_appointment(appointment_id):
    if not _require_admin():
        return redirect("/login?next=/admin/dashboard")

    db = get_db()
    db.execute("""
        UPDATE appointments
        SET status='CANCELLED',
            completed_at=strftime('%s','now')
        WHERE id=? AND status IN ('WAITING','ACCEPTED')
    """, (appointment_id,))
    db.commit()

    return redirect("/admin/dashboard")