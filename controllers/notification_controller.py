from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from controllers.auth_controller import login_required
from models.notification import Notification
from repositories import notification_repository


notification_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@notification_bp.route("", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        notification_repository.create(
            g.db,
            Notification(
                title=request.form.get("title", "").strip(),
                content=request.form.get("content", "").strip(),
                department=request.form.get("department", "").strip() or None,
                status="unread",
            ),
        )
        flash("Tạo thông báo thành công.", "success")
        return redirect(url_for("notifications.index"))

    notifications = notification_repository.get_all(g.db)
    return render_template("notifications.html", notifications=notifications)


@notification_bp.route("/<int:notification_id>/read", methods=["POST"])
@login_required
def mark_read(notification_id):
    notification = notification_repository.get_by_id(g.db, notification_id)

    if not notification:
        flash("Không tìm thấy thông báo.", "danger")
        return redirect(url_for("notifications.index"))

    notification_repository.mark_read(g.db, notification)
    flash("Đã đánh dấu thông báo là đã đọc.", "success")
    return redirect(url_for("notifications.index"))

