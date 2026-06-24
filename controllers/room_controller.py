from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.connection import SessionLocal
from services.room_service import RoomService, VALID_TYPES, VALID_STATUSES
from functools import wraps

room_bp = Blueprint("room", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@room_bp.route("/rooms")
@login_required
def list_rooms():
    status_filter = request.args.get("status", "")
    db = SessionLocal()
    try:
        service = RoomService(db)
        rooms = service.get_by_status(status_filter) if status_filter else service.get_all()
    finally:
        db.close()
    return render_template("rooms/list.html", rooms=rooms,
                           status_filter=status_filter, valid_statuses=VALID_STATUSES)


@room_bp.route("/rooms/create", methods=["GET", "POST"])
@login_required
def create_room():
    if session.get("role") not in ("admin", "manager"):
        flash("Chỉ Admin/Manager mới có quyền thêm phòng.", "danger")
        return redirect(url_for("room.list_rooms"))

    if request.method == "POST":
        room_number = request.form.get("room_number", "").strip()
        room_type   = request.form.get("room_type", "")
        floor       = request.form.get("floor", 1)
        description = request.form.get("description", "").strip()

        db = SessionLocal()
        try:
            service = RoomService(db)
            room, error = service.create(room_number, room_type, floor, description)
            if error:
                flash(error, "danger")
            else:
                flash(f"Đã thêm phòng {room.RoomNumber}", "success")
                return redirect(url_for("room.list_rooms"))
        finally:
            db.close()

    return render_template("rooms/form.html", room=None, action="Thêm phòng",
                           valid_types=VALID_TYPES, valid_statuses=VALID_STATUSES)


@room_bp.route("/rooms/<int:room_id>/edit", methods=["GET", "POST"])
@login_required
def edit_room(room_id):
    db = SessionLocal()
    try:
        service = RoomService(db)
        room = service.get_by_id(room_id)
        if not room:
            flash("Không tìm thấy phòng.", "danger")
            return redirect(url_for("room.list_rooms"))

        if request.method == "POST":
            room_type   = request.form.get("room_type") or None
            status      = request.form.get("status") or None
            floor       = request.form.get("floor") or None
            description = request.form.get("description", "").strip()

            updated, error = service.update(room_id, room_type=room_type,
                                            status=status, floor=floor, description=description)
            if error:
                flash(error, "danger")
            else:
                flash(f"Đã cập nhật phòng {updated.RoomNumber}", "success")
                return redirect(url_for("room.list_rooms"))
    finally:
        db.close()

    return render_template("rooms/form.html", room=room, action="Cập nhật phòng",
                           valid_types=VALID_TYPES, valid_statuses=VALID_STATUSES)


@room_bp.route("/rooms/<int:room_id>/delete", methods=["POST"])
@login_required
def delete_room(room_id):
    db = SessionLocal()
    try:
        service = RoomService(db)
        ok, error = service.delete(room_id, session.get("role", "staff"))
        flash("Đã xóa phòng." if ok else error, "success" if ok else "danger")
    finally:
        db.close()
    return redirect(url_for("room.list_rooms"))
