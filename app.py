from flask import Flask
from database import ensure_db, close_db

from routes.public_routes import public_bp
from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.admin_routes import admin_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret-key-change-me"

    ensure_db()
    app.teardown_appcontext(close_db)

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(admin_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)