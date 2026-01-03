from flask import Blueprint, render_template, redirect, session, request
from services.doctor_service import (
    get_or_link_doctor_for_user,
    update_doctor_status,
    get_doctor_requests,
    get_counts,
    accept_request,
    reject_request,
    start_request,
    complete_request,
    call_next,
)

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")


def _require_doctor():
    # doctor temp login sets session["doctor_id"]
    return session.get("role") == "doctor" and session.get("doctor_id") is not None


def _current_doctor():
    """
    We trust session['doctor_id'] first (temp doctor login).
    If missing, fallback to linking (older flow).
    """
    if session.get("doctor_id"):
        # doctor_service can treat this as doctor id directly
        # BUT to keep compatibility with your service, we return a dict shape with id
        return {"id": session["doctor_id"]}
    # fallback (if you still support doctor users inside users table)
    if session.get("user_id"):
        return get_or_link_doctor_for_user(session["user_id"])
    return None


@doctor_bp.route("/dashboard")
def dashboard():
    if not _require_doctor():
        return redirect("/login")

    doctor = _current_doctor()
    if not doctor:
        return render_template("doctor_panel.html", doctor=None)

    waiting, active, done = get_doctor_requests(doctor["id"])
    active_count, waiting_count = get_counts(doctor["id"])

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
        return redirect("/login")

    doctor = _current_doctor()
    if not doctor:
        return redirect("/doctor/dashboard")

    new_status = request.form.get("status", "AVAILABLE")
    if new_status not in ("AVAILABLE", "BUSY", "OFFLINE"):
        new_status = "AVAILABLE"

    update_doctor_status(doctor["id"], new_status)
    return redirect("/doctor/dashboard")


@doctor_bp.route("/call-next")
def call_next_route():
    if not _require_doctor():
        return redirect("/login")

    doctor = _current_doctor()
    if doctor:
        call_next(doctor["id"])
    return redirect("/doctor/dashboard")


@doctor_bp.route("/accept/<int:appointment_id>")
def accept(appointment_id):
    if not _require_doctor():
        return redirect("/login")
    accept_request(appointment_id)
    return redirect("/doctor/dashboard")


@doctor_bp.route("/reject/<int:appointment_id>")
def reject(appointment_id):
    if not _require_doctor():
        return redirect("/login")
    reject_request(appointment_id)
    return redirect("/doctor/dashboard")


@doctor_bp.route("/start/<int:appointment_id>")
def start(appointment_id):
    if not _require_doctor():
        return redirect("/login")
    start_request(appointment_id)
    return redirect("/doctor/dashboard")


@doctor_bp.route("/complete/<int:appointment_id>")
def complete(appointment_id):
    if not _require_doctor():
        return redirect("/login")
    complete_request(appointment_id)
    return redirect("/doctor/dashboard")
