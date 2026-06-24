from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.connection import SessionLocal
from services.guest_notification_service import GuestNotificationService, VALID_CHANNELS
from services.booking_service import BookingService
from functools import wraps

guest_notif_bp = Blueprint("guest_notif", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


# ── N1-6: Thông báo cho khách hàng ───────────────────────────────────
@guest_notif_bp.route("/guest-notifications")
@login_required
def list_notifications():
    db = SessionLocal()
    try:
        notifications = GuestNotificationService(db).get_all()
    finally:
        db.close()
    return render_template("guest_notifications/list.html", notifications=notifications)


@guest_notif_bp.route("/guest-notifications/create", methods=["GET", "POST"])
@login_required
def create_notification():
    db = SessionLocal()
    try:
        bookings = BookingService(db).get_all()

        if request.method == "POST":
            booking_id = request.form.get("booking_id", "")
            subject    = request.form.get("subject", "").strip()
            content    = request.form.get("content", "").strip()
            channel    = request.form.get("channel", "system")

            if not booking_id or not str(booking_id).isdigit():
                flash("Vui lòng chọn đặt phòng hợp lệ.", "danger")
            else:
                service = GuestNotificationService(db)
                n, error = service.create(int(booking_id), subject, content, channel)
                if error:
                    flash(error, "danger")
                else:
                    flash("Đã gửi thông báo cho khách.", "success")
                    return redirect(url_for("guest_notif.list_notifications"))
    finally:
        db.close()

    return render_template("guest_notifications/form.html",
                           bookings=bookings, channels=VALID_CHANNELS)


@guest_notif_bp.route("/guest-notifications/<int:notif_id>/delete", methods=["POST"])
@login_required
def delete_notification(notif_id):
    if session.get("role") not in ("admin", "manager"):
        flash("Chỉ Admin/Manager mới có quyền xóa thông báo.", "danger")
        return redirect(url_for("guest_notif.list_notifications"))
    db = SessionLocal()
    try:
        ok, error = GuestNotificationService(db).delete(notif_id)
        flash("Đã xóa thông báo." if ok else error, "success" if ok else "danger")
    finally:
        db.close()
    return redirect(url_for("guest_notif.list_notifications"))


@guest_notif_bp.route("/guest-notifications/booking/<int:booking_id>")
def guest_booking_notifications(booking_id):
    db = SessionLocal()
    try:
        booking = BookingService(db).get_by_id(booking_id)
        if not booking:
            flash("Khong tim thay thong tin luu tru.", "danger")
            return redirect(url_for("auth.login"))
        notifications = GuestNotificationService(db).get_by_booking(booking_id)
    finally:
        db.close()
    return render_template(
        "guest_notifications/booking_public.html",
        booking=booking,
        notifications=notifications,
    )
