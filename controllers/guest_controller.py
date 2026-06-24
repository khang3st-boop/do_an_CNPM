from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.connection import SessionLocal
from services.guest_service import GuestService
from services.booking_service import BookingService, VALID_STATUSES as BOOKING_STATUSES
from services.room_service import RoomService
from functools import wraps

guest_bp = Blueprint("guest", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


# ── N1-4: Danh sách khách ──────────────────────────────────────────────
@guest_bp.route("/guests")
@login_required
def list_guests():
    keyword = request.args.get("q", "").strip()
    db = SessionLocal()
    try:
        service = GuestService(db)
        guests = service.search(keyword) if keyword else service.get_all()
    finally:
        db.close()
    return render_template("guests/list.html", guests=guests, keyword=keyword)


@guest_bp.route("/guests/create", methods=["GET", "POST"])
@login_required
def create_guest():
    if request.method == "POST":
        full_name   = request.form.get("full_name", "").strip()
        id_card     = request.form.get("id_card", "").strip()
        phone       = request.form.get("phone", "").strip()
        email       = request.form.get("email", "").strip()
        address     = request.form.get("address", "").strip()
        nationality = request.form.get("nationality", "Việt Nam").strip()

        db = SessionLocal()
        try:
            service = GuestService(db)
            g, error = service.create(full_name, id_card, phone, email, address, nationality)
            if error:
                flash(error, "danger")
            else:
                flash(f"Đã thêm khách: {g.FullName}", "success")
                return redirect(url_for("guest.list_guests"))
        finally:
            db.close()

    return render_template("guests/form.html", guest=None, action="Thêm khách hàng")


@guest_bp.route("/guests/<int:guest_id>/edit", methods=["GET", "POST"])
@login_required
def edit_guest(guest_id):
    db = SessionLocal()
    try:
        service = GuestService(db)
        guest = service.get_by_id(guest_id)
        if not guest:
            flash("Không tìm thấy khách hàng.", "danger")
            return redirect(url_for("guest.list_guests"))

        if request.method == "POST":
            full_name   = request.form.get("full_name", "").strip()
            id_card     = request.form.get("id_card", "").strip()
            phone       = request.form.get("phone", "").strip()
            email       = request.form.get("email", "").strip()
            address     = request.form.get("address", "").strip()
            nationality = request.form.get("nationality", "Việt Nam").strip()

            updated, error = service.update(
                guest_id, full_name, id_card, phone, email, address, nationality
            )
            if error:
                flash(error, "danger")
            else:
                flash(f"Đã cập nhật khách: {updated.FullName}", "success")
                return redirect(url_for("guest.list_guests"))
    finally:
        db.close()

    return render_template("guests/form.html", guest=guest, action="Cập nhật khách hàng")


@guest_bp.route("/guests/<int:guest_id>/delete", methods=["POST"])
@login_required
def delete_guest(guest_id):
    if session.get("role") not in ("admin", "manager"):
        flash("Chỉ Admin/Manager mới có quyền xóa khách hàng.", "danger")
        return redirect(url_for("guest.list_guests"))
    db = SessionLocal()
    try:
        ok, error = GuestService(db).delete(guest_id)
        flash("Đã xóa khách hàng." if ok else error, "success" if ok else "danger")
    finally:
        db.close()
    return redirect(url_for("guest.list_guests"))


# ── N1-4: Đặt phòng ───────────────────────────────────────────────────
@guest_bp.route("/bookings")
@login_required
def list_bookings():
    status_filter = request.args.get("status", "")
    db = SessionLocal()
    try:
        service  = BookingService(db)
        bookings = service.get_by_status(status_filter) if status_filter else service.get_all()
    finally:
        db.close()
    return render_template("bookings/list.html", bookings=bookings,
                           status_filter=status_filter, valid_statuses=BOOKING_STATUSES)


@guest_bp.route("/bookings/create", methods=["GET", "POST"])
@login_required
def create_booking():
    db = SessionLocal()
    try:
        guests = GuestService(db).get_all()
        rooms  = RoomService(db).get_by_status("available")

        if request.method == "POST":
            guest_id    = request.form.get("guest_id")
            room_id     = request.form.get("room_id")
            check_in    = request.form.get("check_in", "")
            check_out   = request.form.get("check_out", "")
            notes       = request.form.get("notes", "").strip()
            total_price = request.form.get("total_price", 0)

            if not guest_id or not room_id:
                flash("Vui lòng chọn khách hàng và phòng.", "danger")
            else:
                service = BookingService(db)
                b, error = service.create(
                    int(guest_id), int(room_id), check_in, check_out, notes, total_price
                )
                if error:
                    flash(error, "danger")
                else:
                    flash(f"Đã tạo đặt phòng #{b.BookingID}", "success")
                    return redirect(url_for("guest.list_bookings"))
    finally:
        db.close()

    return render_template("bookings/form.html", booking=None,
                           guests=guests, rooms=rooms, action="Tạo đặt phòng")


@guest_bp.route("/bookings/<int:booking_id>/edit", methods=["GET", "POST"])
@login_required
def edit_booking(booking_id):
    if session.get("role") not in ("admin", "manager"):
        flash("Chỉ Admin/Manager mới có quyền sửa đặt phòng.", "danger")
        return redirect(url_for("guest.list_bookings"))

    db = SessionLocal()
    try:
        service = BookingService(db)
        booking = service.get_by_id(booking_id)
        if not booking:
            flash("Không tìm thấy đặt phòng.", "danger")
            return redirect(url_for("guest.list_bookings"))

        guests = GuestService(db).get_all()
        rooms  = RoomService(db).get_all()

        if request.method == "POST":
            check_in    = request.form.get("check_in", "")
            check_out   = request.form.get("check_out", "")
            notes       = request.form.get("notes", "").strip()
            total_price = request.form.get("total_price", 0)

            updated, error = service.update(booking_id, check_in, check_out, notes, total_price)
            if error:
                flash(error, "danger")
            else:
                flash(f"Đã cập nhật đặt phòng #{updated.BookingID}", "success")
                return redirect(url_for("guest.list_bookings"))
    finally:
        db.close()

    return render_template("bookings/form.html", booking=booking,
                           guests=guests, rooms=rooms, action="Cập nhật đặt phòng")


@guest_bp.route("/bookings/<int:booking_id>/status", methods=["POST"])
@login_required
def change_booking_status(booking_id):
    new_status = request.form.get("status", "")
    db = SessionLocal()
    try:
        service = BookingService(db)
        _, error = service.change_status(booking_id, new_status, session.get("role", "staff"))
        if error:
            flash(error, "danger")
        else:
            labels = {
                "confirmed": "Đã xác nhận",
                "checked_in": "Đã nhận phòng",
                "checked_out": "Đã trả phòng",
                "cancelled": "Đã huỷ",
            }
            flash(f"Trạng thái đặt phòng: {labels.get(new_status, new_status)}", "success")
    finally:
        db.close()
    return redirect(url_for("guest.list_bookings"))


@guest_bp.route("/bookings/<int:booking_id>/delete", methods=["POST"])
@login_required
def delete_booking(booking_id):
    db = SessionLocal()
    try:
        ok, error = BookingService(db).delete(booking_id, session.get("role", "staff"))
        flash("Đã xóa đặt phòng." if ok else error, "success" if ok else "danger")
    finally:
        db.close()
    return redirect(url_for("guest.list_bookings"))
