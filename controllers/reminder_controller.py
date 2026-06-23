from datetime import datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from controllers.auth_controller import login_required
from models.reminder import Reminder
from repositories import reminder_repository, room_repository


reminder_bp = Blueprint("reminders", __name__, url_prefix="/reminders")


@reminder_bp.route("", methods=["GET", "POST"])
@login_required
def index():
    rooms = room_repository.get_active(g.db)

    if request.method == "POST":
        reminder_repository.create(
            g.db,
            Reminder(
                title=request.form.get("title", "").strip(),
                content=request.form.get("content", "").strip() or None,
                room_id=int(request.form.get("room_id") or 0) or None,
                guest_name=request.form.get("guest_name", "").strip() or None,
                reminder_type=request.form.get("reminder_type", "general"),
                reminder_time=datetime.fromisoformat(request.form.get("reminder_time")),
                status="pending",
            ),
        )
        flash("Tạo lịch nhắc thành công.", "success")
        return redirect(url_for("reminders.index"))

    reminders = reminder_repository.get_all(g.db)
    room_map = {room.id: room for room in room_repository.get_all(g.db)}
    return render_template("reminders.html", reminders=reminders, rooms=rooms, room_map=room_map)


@reminder_bp.route("/<int:reminder_id>/status", methods=["POST"])
@login_required
def update_status(reminder_id):
    reminder = reminder_repository.get_by_id(g.db, reminder_id)

    if not reminder:
        flash("Không tìm thấy lịch nhắc.", "danger")
        return redirect(url_for("reminders.index"))

    reminder_repository.update_status(g.db, reminder, request.form.get("status", "pending"))
    flash("Cập nhật trạng thái lịch nhắc thành công.", "success")
    return redirect(url_for("reminders.index"))

