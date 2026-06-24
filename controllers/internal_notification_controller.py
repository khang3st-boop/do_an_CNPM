from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from database.connection import SessionLocal
from services.internal_notification_service import (
    InternalNotificationService,
    VALID_DEPARTMENTS,
    VALID_PRIORITIES,
)
from services.user_service import UserService

internal_notif_bp = Blueprint("internal_notif", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui long dang nhap.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@internal_notif_bp.route("/internal-notifications")
@login_required
def list_notifications():
    db = SessionLocal()
    try:
        user = UserService(db).get_user_by_id(session["user_id"])
        department = getattr(user, "Department", "") if user else ""
        notifications = InternalNotificationService(db).get_for_user(
            session["user_id"],
            department,
        )
    finally:
        db.close()
    return render_template("internal_notifications/list.html", notifications=notifications)


@internal_notif_bp.route("/internal-notifications/create", methods=["GET", "POST"])
@login_required
def create_notification():
    db = SessionLocal()
    try:
        users = UserService(db).get_all_users()
        users = [u for u in users if u.UserID != session["user_id"]]

        if request.method == "POST":
            target_type = request.form.get("target_type", "all")
            to_user_id = request.form.get("to_user_id", "")
            to_department = request.form.get("to_department", "")
            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()
            priority = request.form.get("priority", "normal")

            if target_type != "user":
                to_user_id = None
            if target_type != "department":
                to_department = None

            _, error = InternalNotificationService(db).create(
                session["user_id"],
                to_user_id if to_user_id else None,
                title,
                content,
                priority,
                to_department if to_department else None,
            )
            if error:
                flash(error, "danger")
            else:
                flash("Da gui thong bao noi bo.", "success")
                return redirect(url_for("internal_notif.list_notifications"))
    finally:
        db.close()

    return render_template(
        "internal_notifications/form.html",
        users=users,
        priorities=VALID_PRIORITIES,
        departments=VALID_DEPARTMENTS,
    )


@internal_notif_bp.route("/internal-notifications/<int:notif_id>/read", methods=["POST"])
@login_required
def mark_notification_read(notif_id):
    db = SessionLocal()
    try:
        InternalNotificationService(db).mark_read(notif_id, session["user_id"])
        flash("Da xac nhan da doc thong bao.", "success")
    finally:
        db.close()
    return redirect(url_for("internal_notif.list_notifications"))


@internal_notif_bp.route("/internal-notifications/<int:notif_id>/delete", methods=["POST"])
@login_required
def delete_notification(notif_id):
    db = SessionLocal()
    try:
        service = InternalNotificationService(db)
        ok, error = service.delete(notif_id, session["user_id"], session.get("role", "staff"))
        flash("Da xoa thong bao." if ok else error, "success" if ok else "danger")
    finally:
        db.close()
    return redirect(url_for("internal_notif.list_notifications"))


@internal_notif_bp.route("/api/notifications/unread-count")
@login_required
def unread_count():
    from flask import jsonify

    db = SessionLocal()
    try:
        user = UserService(db).get_user_by_id(session["user_id"])
        department = getattr(user, "Department", "") if user else ""
        count = InternalNotificationService(db).count_unread(session["user_id"], department)
    finally:
        db.close()
    return jsonify({"count": count})


@internal_notif_bp.route("/api/internal-notifications/unread")
@login_required
def unread_internal_notifications():
    from flask import jsonify

    db = SessionLocal()
    try:
        user = UserService(db).get_user_by_id(session["user_id"])
        department = getattr(user, "Department", "") if user else ""
        notifications = InternalNotificationService(db).get_for_user(
            session["user_id"],
            department,
        )
        data = []
        for notif in notifications:
            if getattr(notif, "UserRead", False):
                continue
            data.append({
                "id": notif.NotifID,
                "title": notif.Title,
                "content": notif.Content,
                "priority": notif.Priority,
                "sender": notif.sender.Username if notif.sender else "",
                "time": notif.CreatedAt.strftime("%d/%m/%Y %H:%M") if notif.CreatedAt else "",
            })
    finally:
        db.close()
    return jsonify(data)


@internal_notif_bp.route("/api/internal-notifications/<int:notif_id>/read", methods=["POST"])
@login_required
def api_mark_internal_notification_read(notif_id):
    from flask import jsonify

    db = SessionLocal()
    try:
        InternalNotificationService(db).mark_read(notif_id, session["user_id"])
    finally:
        db.close()
    return jsonify({"success": True})
