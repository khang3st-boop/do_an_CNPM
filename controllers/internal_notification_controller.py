from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.connection import SessionLocal
from services.internal_notification_service import InternalNotificationService, VALID_PRIORITIES
from services.user_service import UserService
from functools import wraps

internal_notif_bp = Blueprint("internal_notif", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


# ── N1-5: Thông báo nội bộ ────────────────────────────────────────────
@internal_notif_bp.route("/internal-notifications")
@login_required
def list_notifications():
    db = SessionLocal()
    try:
        service = InternalNotificationService(db)
        notifications = service.get_for_user(session["user_id"])
        # Đánh dấu tất cả là đã đọc khi vào trang
        for n in notifications:
            if not n.IsRead:
                service.mark_read(n.NotifID)
    finally:
        db.close()
    return render_template("internal_notifications/list.html", notifications=notifications)


@internal_notif_bp.route("/internal-notifications/create", methods=["GET", "POST"])
@login_required
def create_notification():
    db = SessionLocal()
    try:
        users = UserService(db).get_all_users()
        # Loại bỏ chính mình
        users = [u for u in users if u.UserID != session["user_id"]]

        if request.method == "POST":
            to_user_id = request.form.get("to_user_id", "")   # "" = broadcast
            title      = request.form.get("title", "").strip()
            content    = request.form.get("content", "").strip()
            priority   = request.form.get("priority", "normal")

            service = InternalNotificationService(db)
            n, error = service.create(
                session["user_id"],
                to_user_id if to_user_id else None,
                title, content, priority
            )
            if error:
                flash(error, "danger")
            else:
                flash("Đã gửi thông báo nội bộ.", "success")
                return redirect(url_for("internal_notif.list_notifications"))
    finally:
        db.close()

    return render_template("internal_notifications/form.html",
                           users=users, priorities=VALID_PRIORITIES)


@internal_notif_bp.route("/internal-notifications/<int:notif_id>/delete", methods=["POST"])
@login_required
def delete_notification(notif_id):
    db = SessionLocal()
    try:
        service = InternalNotificationService(db)
        ok, error = service.delete(notif_id, session["user_id"], session.get("role", "staff"))
        flash("Đã xóa thông báo." if ok else error, "success" if ok else "danger")
    finally:
        db.close()
    return redirect(url_for("internal_notif.list_notifications"))


# API: đếm số thông báo chưa đọc (dùng cho badge nav)
@internal_notif_bp.route("/api/notifications/unread-count")
@login_required
def unread_count():
    from flask import jsonify
    db = SessionLocal()
    try:
        count = InternalNotificationService(db).count_unread(session["user_id"])
    finally:
        db.close()
    return jsonify({"count": count})
