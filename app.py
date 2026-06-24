import os
from flask import Flask
from dotenv import load_dotenv
from database.connection import Base, engine, test_connection
from controllers.auth_controller import auth_bp
from controllers.reminder_controller import reminder_bp
from controllers.user_controller import user_bp
from controllers.room_controller import room_bp
from controllers.guest_controller import guest_bp
from controllers.internal_notification_controller import internal_notif_bp
from controllers.guest_notification_controller import guest_notif_bp
from controllers.housekeeping_controller import housekeeping_bp
from controllers.report_controller import report_bp
from controllers.api_controller import api_bp
from controllers.react_controller import react_bp
from scheduler.reminder_scheduler import start_scheduler, stop_scheduler
import atexit

load_dotenv()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.getenv("SECRET_KEY", "fallback_secret_key")

    app.register_blueprint(auth_bp)
    app.register_blueprint(reminder_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(guest_bp)
    app.register_blueprint(internal_notif_bp)
    app.register_blueprint(guest_notif_bp)
    app.register_blueprint(housekeeping_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(react_bp)

    return app


def init_db():
    from models import user, reminder, notification, room, guest, booking, internal_notification, guest_notification, housekeeping_task  # noqa: F401
    Base.metadata.create_all(bind=engine)
    print("[DB] Đã kiểm tra / tạo bảng thành công.")


def seed_data():
    from database.connection import SessionLocal
    from services.auth_service import AuthService
    from services.room_service import RoomService

    db = SessionLocal()
    try:
        # Seed admin
        auth = AuthService(db)
        user, _ = auth.create_user("admin", "admin123", "admin@hotel.com", "admin")
        if user:
            print("[SEED] Tài khoản admin: admin / admin123")

        # Seed manager
        mgr, _ = auth.create_user("manager1", "manager123", "manager@hotel.com", "manager")
        if mgr:
            print("[SEED] Tài khoản manager: manager1 / manager123")

        # Seed phòng mẫu
        room_svc = RoomService(db)
        sample_rooms = [
            ("101", "Standard", 1, "Phòng tiêu chuẩn tầng 1"),
            ("201", "Deluxe", 2, "Phòng deluxe view sân vườn"),
            ("301", "VIP", 3, "Phòng VIP góc nhìn toàn cảnh"),
            ("401", "Suite", 4, "Phòng Suite hạng sang"),
        ]
        for num, rtype, floor, desc in sample_rooms:
            r, _ = room_svc.create(num, rtype, floor, desc)
            if r:
                print(f"[SEED] Phòng {r.RoomNumber} - {r.RoomType}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("  HOTEL REMINDER SYSTEM — khởi động...")
    print("=" * 50)

    if not test_connection():
        print("[ERROR] Không kết nối được SQL Server. Kiểm tra lại file .env")
        exit(1)

    init_db()
    seed_data()
    start_scheduler()
    atexit.register(stop_scheduler)

    app = create_app()
    print("[FLASK] Đang chạy tại http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
