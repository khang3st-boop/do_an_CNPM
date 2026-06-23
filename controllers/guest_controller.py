from datetime import datetime

from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from controllers.auth_controller import login_required
from models.guest import Guest
from repositories import guest_repository, room_repository


guest_bp = Blueprint("guests", __name__, url_prefix="/guests")


def parse_datetime(value):
    if not value:
        return None
    return datetime.fromisoformat(value)


@guest_bp.route("", methods=["GET", "POST"])
@login_required
def index():
    active_rooms = room_repository.get_active(g.db)

    if request.method == "POST":
        room_id = int(request.form.get("room_id") or 0)
        room = room_repository.get_by_id(g.db, room_id)

        if not room or not room.is_active:
            flash("Phòng không tồn tại hoặc đã bị vô hiệu hóa.", "danger")
            return redirect(url_for("guests.index"))

        guest_repository.create(
            g.db,
            Guest(
                full_name=request.form.get("full_name", "").strip(),
                phone=request.form.get("phone", "").strip() or None,
                email=request.form.get("email", "").strip().lower() or None,
                identity_number=request.form.get("identity_number", "").strip() or None,
                room_id=room_id,
                check_in_date=parse_datetime(request.form.get("check_in_date")),
                check_out_date=parse_datetime(request.form.get("check_out_date")),
                is_active=True,
            ),
        )
        flash("Tạo thông tin khách lưu trú thành công.", "success")
        return redirect(url_for("guests.index"))

    guests = guest_repository.get_all(g.db)
    room_map = {room.id: room for room in room_repository.get_all(g.db)}
    return render_template("guests.html", guests=guests, rooms=active_rooms, room_map=room_map)


@guest_bp.route("/<int:guest_id>/toggle-status", methods=["POST"])
@login_required
def toggle_status(guest_id):
    guest = guest_repository.get_by_id(g.db, guest_id)

    if not guest:
        flash("Không tìm thấy khách lưu trú.", "danger")
        return redirect(url_for("guests.index"))

    guest_repository.update(g.db, guest, {"is_active": not guest.is_active})
    flash("Cập nhật trạng thái khách lưu trú thành công.", "success")
    return redirect(url_for("guests.index"))

