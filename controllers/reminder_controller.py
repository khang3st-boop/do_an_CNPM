from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.connection import SessionLocal
from services.reminder_service import ReminderService
from functools import wraps

reminder_bp = Blueprint("reminder", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập để tiếp tục.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@reminder_bp.route("/")
@reminder_bp.route("/dashboard")
@login_required
def dashboard():
    db = SessionLocal()
    try:
        service = ReminderService(db)
        upcoming = service.get_upcoming(session["user_id"])
        all_reminders = service.get_all(session["user_id"])
    finally:
        db.close()
    return render_template("dashboard.html", upcoming=upcoming, all_reminders=all_reminders)


@reminder_bp.route("/reminders")
@login_required
def list_reminders():
    db = SessionLocal()
    try:
        service = ReminderService(db)
        reminders = service.get_all(session["user_id"])
    finally:
        db.close()
    return render_template("reminders/list.html", reminders=reminders)


from services.booking_service import BookingService

@reminder_bp.route("/reminders/create", methods=["GET", "POST"])
@login_required
def create_reminder():
    db = SessionLocal()
    try:
        bookings = BookingService(db).get_all()
    finally:
        db.close()

    if request.method == "POST":
        title         = request.form.get("title", "")
        description   = request.form.get("description", "")
        time_str      = request.form.get("reminder_time", "")
        reminder_type = request.form.get("reminder_type", "custom")
        booking_id    = request.form.get("booking_id", "")

        db = SessionLocal()
        try:
            service = ReminderService(db)
            r, error = service.create(session["user_id"], title, description, time_str, reminder_type, booking_id)
            if error:
                flash(error, "danger")
            else:
                flash(f"Đã thêm lịch nhắc: {r.Title}", "success")
                return redirect(url_for("reminder.list_reminders"))
        finally:
            db.close()

    return render_template("reminders/form.html", reminder=None, bookings=bookings, action="Thêm mới")


@reminder_bp.route("/reminders/<int:reminder_id>/edit", methods=["GET", "POST"])
@login_required
def edit_reminder(reminder_id):
    db = SessionLocal()
    try:
        service = ReminderService(db)
        reminder = service.get_by_id(reminder_id, session["user_id"])
        if not reminder:
            flash("Không tìm thấy lịch nhắc.", "danger")
            return redirect(url_for("reminder.list_reminders"))

        bookings = BookingService(db).get_all()

        if request.method == "POST":
            title         = request.form.get("title", "")
            description   = request.form.get("description", "")
            time_str      = request.form.get("reminder_time", "")
            reminder_type = request.form.get("reminder_type", "custom")
            booking_id    = request.form.get("booking_id", "")
            r, error = service.update(reminder_id, session["user_id"], title, description, time_str, reminder_type, booking_id)
            if error:
                flash(error, "danger")
            else:
                flash(f"Đã cập nhật: {r.Title}", "success")
                return redirect(url_for("reminder.list_reminders"))
    finally:
        db.close()

    return render_template("reminders/form.html", reminder=reminder, bookings=bookings, action="Cập nhật")


@reminder_bp.route("/reminders/<int:reminder_id>/delete", methods=["POST"])
@login_required
def delete_reminder(reminder_id):
    db = SessionLocal()
    try:
        service = ReminderService(db)
        ok, error = service.delete(reminder_id, session["user_id"])
        if ok:
            flash("Đã xóa lịch nhắc.", "success")
        else:
            flash(error, "danger")
    finally:
        db.close()
    return redirect(url_for("reminder.list_reminders"))

@reminder_bp.route("/reminders/<int:reminder_id>/status", methods=["POST"])
@login_required
def update_status(reminder_id):
    status = request.form.get("status", "Hoàn thành")
    db = SessionLocal()
    try:
        service = ReminderService(db)
        ok, error = service.update_status(reminder_id, session["user_id"], status)
        if ok:
            flash(f"Đã cập nhật trạng thái thành: {status}", "success")
        else:
            flash(error, "danger")
    finally:
        db.close()
    return redirect(url_for("reminder.list_reminders"))

from flask import jsonify
from repositories.notification_repository import NotificationRepository

@reminder_bp.route("/api/notifications/unread", methods=["GET"])
@login_required
def get_unread_notifications():
    db = SessionLocal()
    try:
        repo = NotificationRepository(db)
        unreads = repo.get_unread_by_user(session["user_id"])
        data = []
        for n in unreads:
            data.append({
                "id": n.NotificationID,
                "title": n.reminder.Title,
                "time": n.SentTime.strftime("%d/%m/%Y %H:%M")
            })
        return jsonify(data)
    finally:
        db.close()

@reminder_bp.route("/api/notifications/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notification_id):
    db = SessionLocal()
    try:
        repo = NotificationRepository(db)
        repo.mark_read(notification_id)
        return jsonify({"success": True})
    finally:
        db.close()
