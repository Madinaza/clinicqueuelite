from flask import Blueprint, render_template, request, redirect, session
from services.auth_service import authenticate, register_patient, email_exists, update_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    next_url = request.args.get("next") or ""

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = authenticate(email, password)
        if not user:
            return render_template("login.html", error="Invalid email or password")

        session.clear()
        session["user_id"] = user["id"]
        session["email"] = user["email"]
        session["role"] = user["role"]
        session["doctor_id"] = user.get("doctor_id")

        if next_url:
            return redirect(next_url)

        if user["role"] == "patient":
            return redirect("/patient/dashboard")
        if user["role"] == "doctor":
            return redirect("/doctor/dashboard")
        if user["role"] == "ADMIN":
            return redirect("/admin/dashboard")

        return redirect("/")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if password != confirm:
            return render_template("register.html", error="Passwords do not match")

        if email_exists(email):
            return render_template("register.html", error="Email already registered.")

        ok = register_patient(email, password)
        if not ok:
            return render_template("register.html", error="Could not register. Try again.")

        return redirect("/login")

    return render_template("register.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if not email_exists(email):
            return render_template("forgot_password.html", error="Email not found")

        session["reset_email"] = email
        return redirect("/reset-password")

    return render_template("forgot_password.html")


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    email = session.get("reset_email")
    if not email:
        return redirect("/login")

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if password != confirm:
            return render_template("reset_password.html", error="Passwords do not match")

        update_password(email, password)
        session.pop("reset_email", None)
        return redirect("/login")

    return render_template("reset_password.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
