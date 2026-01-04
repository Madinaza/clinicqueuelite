from flask import Blueprint, render_template, redirect, session, request
from services.doctor_service import (
    get_current_doctor_id_from_session,
    get_doctor,
    update_doctor_status,
    get_doctor_requests,
    get_counts,
    accept_request,
    reject_request,
    start_request,
    complete_request,
    call_next,
    update_note,
)

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")


def _require_doctor():
    return session.get("user_id") and session.get("role") == "doctor"


@doctor_bp.route("/dashboard")
def dashboard():
    if not _require_doctor():
        return redirect("/login?next=/doctor/dashboard")

    doctor_id = get_current_doctor_id_from_session(session)
    if not doctor_id:
        return render_template("doctor_panel.html", doctor=None)

    doctor = get_doctor(doctor_id)
    waiting, active, done = get_doctor_requests(doctor_id)
    active_count, waiting_count = get_counts(doctor_id)

    return render_template(
        "doctor_panel.html",
        doctor=doctor,
        waiting=waiting,
        active=active,
        done=done,
        active_count=active_count,
        waiting_count=waiting_count,
    )


@doctor_bp.route("/status", methods=["POST"])
def status():
    if not _require_doctor():
        return redirect("/login?next=/doctor/dashboard")

    doctor_id = get_current_doctor_id_from_session(session)
    if not doctor_id:
        return redirect("/doctor/dashboard")

    new_status = request.form.get("status", "AVAILABLE")
    if new_status not in ("AVAILABLE", "BUSY", "OFFLINE"):
        new_status = "AVAILABLE"

    update_doctor_status(doctor_id, new_status)
    return redirect("/doctor/dashboard")


@doctor_bp.route("/call-next")
def call_next_route():
    if not _require_doctor():
        return redirect("/login?next=/doctor/dashboard")

    doctor_id = get_current_doctor_id_from_session(session)
    if doctor_id:
        call_next(doctor_id)
    return redirect("/doctor/dashboard")


@doctor_bp.route("/accept/<int:appointment_id>")
def accept(appointment_id):
    if not _require_doctor():
        return redirect("/login?next=/doctor/dashboard")

    doctor_id = get_current_doctor_id_from_session(session)
    accept_request(appointment_id, doctor_id)
    return redirect("/doctor/dashboard")


@doctor_bp.route("/reject/<int:appointment_id>")
def reject(appointment_id):
    if not _require_doctor():
        return redirect("/login?next=/doctor/dashboard")

    doctor_id = get_current_doctor_id_from_session(session)
    reject_request(appointment_id, doctor_id)
    return redirect("/doctor/dashboard")


@doctor_bp.route("/start/<int:appointment_id>")
def start(appointment_id):
    if not _require_doctor():
        return redirect("/login?next=/doctor/dashboard")

    doctor_id = get_current_doctor_id_from_session(session)
    start_request(appointment_id, doctor_id)
    return redirect("/doctor/dashboard")


@doctor_bp.route("/complete/<int:appointment_id>")
def complete(appointment_id):
    if not _require_doctor():
        return redirect("/login?next=/doctor/dashboard")

    doctor_id = get_current_doctor_id_from_session(session)
    complete_request(appointment_id, doctor_id)
    return redirect("/doctor/dashboard")


@doctor_bp.route("/note/<int:appointment_id>", methods=["POST"])
def note(appointment_id):
    if not _require_doctor():
        return redirect("/login?next=/doctor/dashboard")

    doctor_id = get_current_doctor_id_from_session(session)
    note_text = request.form.get("note", "").strip()
    update_note(appointment_id, doctor_id, note_text)
    return redirect("/doctor/dashboard")
