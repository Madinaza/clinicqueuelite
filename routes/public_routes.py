from flask import Blueprint, render_template, session
from database import get_db

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    db = get_db()

    doctors = db.execute("""
        SELECT
            d.id,
            d.name,
            d.branch,
            d.experience,
            d.address,
            d.status,

            (
              SELECT COUNT(*)
              FROM appointments a2
              WHERE a2.doctor_id = d.id
                AND a2.status IN ('WAITING','ACCEPTED','IN_PROGRESS')
            ) AS active_requests,

            COALESCE(
                ROUND(AVG(
                    CASE
                        WHEN a.responded_at IS NOT NULL
                        THEN (a.responded_at - a.created_at) / 60.0
                    END
                ), 1),
                5
            ) AS avg_response_minutes

        FROM doctors d
        LEFT JOIN appointments a ON a.doctor_id = d.id
        GROUP BY d.id
        ORDER BY d.id ASC
    """).fetchall()

    waiting_doctor_ids = set()
    if session.get("user_id") and session.get("role") == "patient":
        rows = db.execute("""
            SELECT doctor_id
            FROM appointments
            WHERE patient_id=? AND status='WAITING'
        """, (session["user_id"],)).fetchall()
        waiting_doctor_ids = {r["doctor_id"] for r in rows}

    return render_template("home.html", doctors=doctors, waiting_doctor_ids=waiting_doctor_ids)
