from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from controllers.auth_controller import login_required
from models.room import Room
from repositories import room_repository


room_bp = Blueprint("rooms", __name__, url_prefix="/rooms")


@room_bp.route("", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        room_number = request.form.get("room_number", "").strip()

        if room_repository.get_by_room_number(g.db, room_number):
            flash("Số phòng đã tồn tại.", "danger")
            return redirect(url_for("rooms.index"))

        room_repository.create(
            g.db,
            Room(
                room_number=room_number,
                room_type=request.form.get("room_type", "Standard").strip(),
                floor=int(request.form.get("floor") or 0),
                capacity=int(request.form.get("capacity") or 2),
                price_per_night=float(request.form.get("price_per_night") or 0),
                status=request.form.get("status", "available"),
                is_active=True,
                note=request.form.get("note", "").strip() or None,
            ),
        )
        flash("Tạo phòng mới thành công.", "success")
        return redirect(url_for("rooms.index"))

    rooms = room_repository.get_all(g.db)
    return render_template("rooms.html", rooms=rooms)


@room_bp.route("/<int:room_id>/deactivate", methods=["POST"])
@login_required
def deactivate(room_id):
    room = room_repository.get_by_id(g.db, room_id)

    if not room:
        flash("Không tìm thấy phòng.", "danger")
        return redirect(url_for("rooms.index"))

    room_repository.deactivate(g.db, room)
    flash("Đã vô hiệu hóa phòng.", "success")
    return redirect(url_for("rooms.index"))

