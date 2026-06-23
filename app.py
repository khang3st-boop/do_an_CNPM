import os

from flask import Flask, g

import models
from controllers.auth_controller import auth_bp
from controllers.dashboard_controller import dashboard_bp
from controllers.guest_controller import guest_bp
from controllers.notification_controller import notification_bp
from controllers.reminder_controller import reminder_bp
from controllers.room_controller import room_bp
from controllers.user_controller import user_bp
from database.connection import SessionLocal, init_database
from services.seed_service import seed_default_data


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "hotel-reminder-dev-secret")

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(guest_bp)
    app.register_blueprint(reminder_bp)
    app.register_blueprint(notification_bp)

    @app.before_request
    def open_database_session():
        g.db = SessionLocal()

    @app.teardown_request
    def close_database_session(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()
        SessionLocal.remove()

    with app.app_context():
        init_database()
        db = SessionLocal()
        try:
            seed_default_data(db)
        finally:
            db.close()
            SessionLocal.remove()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

