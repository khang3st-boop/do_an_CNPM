from apscheduler.schedulers.background import BackgroundScheduler
from database.connection import SessionLocal
from repositories.reminder_repository import ReminderRepository
from repositories.notification_repository import NotificationRepository
from datetime import datetime

scheduler = BackgroundScheduler()


def check_reminders():
    """Chạy mỗi 1 phút: kiểm tra và thông báo các lịch đã đến giờ."""
    db = SessionLocal()
    try:
        reminder_repo      = ReminderRepository(db)
        notification_repo  = NotificationRepository(db)

        due_reminders = reminder_repo.get_pending_due()
        for r in due_reminders:
            print(f"[NHẮC LỊCH] {datetime.now().strftime('%H:%M:%S')} | {r.Title} | {r.ReminderTime.strftime('%d/%m/%Y %H:%M')}")
            reminder_repo.mark_sent(r.ReminderID)
            notification_repo.create(r.ReminderID)

        # Xử lý quá hạn
        overdue_reminders = reminder_repo.get_overdue_reminders()
        for r in overdue_reminders:
            print(f"[QUÁ HẠN] {r.Title}")
            reminder_repo.update_status(r.ReminderID, "Quá hạn")
    except Exception as e:
        print(f"[SCHEDULER ERROR] {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(check_reminders, "interval", minutes=1, id="reminder_check")
    scheduler.start()
    print("[SCHEDULER] Đã khởi động — kiểm tra lịch mỗi 1 phút.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("[SCHEDULER] Đã dừng.")
