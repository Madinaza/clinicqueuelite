from flask import Blueprint, render_template, request, redirect, session
from services.admin_service import (
    get_admin_stats,
    list_doctors,
    add_doctor,
    update_doctor_status,
    delete_doctor,
    list_appointments,
    admin_set_appointment_status,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _require_admin():
    return session.get("user_id") and session.get("role") == "ADMIN"


@admin_bp.route("/dashboard")
def dashboard():
    if not _require_admin():
        return redirect("/login")

    stats = get_admin_stats()
    doctors = list_doctors()
    appointments = list_appointments(limit=200)

    return render_template(
        "admin_panel.html",
        stats=stats,
        doctors=doctors,
        appointments=appointments
    )


@admin_bp.route("/doctor/add", methods=["POST"])
def doctor_add():
    if not _require_admin():
        return redirect("/login")

    name = request.form.get("name", "").strip()
    branch = request.form.get("branch", "").strip()
    experience = request.form.get("experience", "").strip()
    address = request.form.get("address", "").strip()
    status = request.form.get("status", "AVAILABLE").strip().upper()

    if not name or not branch or not experience.isdigit() or not address:
        return redirect("/admin/dashboard")

    add_doctor(name, branch, int(experience), address, status)
    return redirect("/admin/dashboard")


@admin_bp.route("/doctor/status", methods=["POST"])
def doctor_status():
    if not _require_admin():
        return redirect("/login")

    doctor_id = request.form.get("doctor_id", "").strip()
    status = request.form.get("status", "AVAILABLE").strip().upper()

    if doctor_id.isdigit():
        update_doctor_status(int(doctor_id), status)

    return redirect("/admin/dashboard")


@admin_bp.route("/doctor/delete/<int:doctor_id>", methods=["POST"])
def doctor_delete(doctor_id):
    if not _require_admin():
        return redirect("/login")

    delete_doctor(doctor_id)
    return redirect("/admin/dashboard")


@admin_bp.route("/appointment/status", methods=["POST"])
def appointment_status():
    if not _require_admin():
        return redirect("/login")

    appointment_id = request.form.get("appointment_id", "").strip()
    new_status = request.form.get("status", "").strip().upper()

    if appointment_id.isdigit() and new_status:
        admin_set_appointment_status(int(appointment_id), new_status)

    return redirect("/admin/dashboard")
