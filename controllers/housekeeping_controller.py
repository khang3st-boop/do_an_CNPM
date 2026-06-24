from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.connection import SessionLocal
from services.housekeeping_service import HousekeepingService
from services.room_service import RoomService
from services.user_service import UserService
from repositories.housekeeping_repository import (
    VALID_TASK_TYPES, VALID_TASK_STATUSES, VALID_PRIORITIES
)
from functools import wraps

housekeeping_bp = Blueprint("housekeeping", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


# ── N1-8: Danh sách lịch dọn / bảo trì ───────────────────────────────
@housekeeping_bp.route("/housekeeping")
@login_required
def list_tasks():
    status_filter = request.args.get("status", "")
    db = SessionLocal()
    try:
        service = HousekeepingService(db)
        role = session.get("role", "staff")
        if role == "staff":
            # Staff chỉ thấy task của mình
            tasks = service.get_by_staff(session["user_id"])
            if status_filter:
                tasks = [t for t in tasks if t.Status == status_filter]
        else:
            tasks = service.get_by_status(status_filter) if status_filter else service.get_all()

        counts = service.count_by_status()
    finally:
        db.close()
    return render_template("housekeeping/list.html", tasks=tasks,
                           status_filter=status_filter,
                           valid_statuses=VALID_TASK_STATUSES,
                           counts=counts)


@housekeeping_bp.route("/housekeeping/create", methods=["GET", "POST"])
@login_required
def create_task():
    if session.get("role") not in ("admin", "manager"):
        flash("Chỉ Admin/Manager mới có quyền tạo công việc.", "danger")
        return redirect(url_for("housekeeping.list_tasks"))

    db = SessionLocal()
    try:
        rooms = RoomService(db).get_all()
        staff = UserService(db).get_all_users()

        if request.method == "POST":
            room_id        = request.form.get("room_id", "")
            assigned_to_id = request.form.get("assigned_to_id", "")
            task_type      = request.form.get("task_type", "")
            description    = request.form.get("description", "").strip()
            scheduled_at   = request.form.get("scheduled_at", "")
            priority       = request.form.get("priority", "normal")

            if not room_id:
                flash("Vui lòng chọn phòng.", "danger")
            else:
                service = HousekeepingService(db)
                t, error = service.create(
                    int(room_id), assigned_to_id, task_type,
                    description, scheduled_at, priority,
                    session.get("role", "staff")
                )
                if error:
                    flash(error, "danger")
                else:
                    flash(f"Đã tạo công việc #{t.TaskID}", "success")
                    return redirect(url_for("housekeeping.list_tasks"))
    finally:
        db.close()

    return render_template("housekeeping/form.html",
                           task=None, rooms=rooms, staff=staff,
                           task_types=VALID_TASK_TYPES,
                           priorities=VALID_PRIORITIES,
                           action="Tạo công việc mới")


@housekeeping_bp.route("/housekeeping/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    if session.get("role") not in ("admin", "manager"):
        flash("Chỉ Admin/Manager mới có quyền sửa công việc.", "danger")
        return redirect(url_for("housekeeping.list_tasks"))

    db = SessionLocal()
    try:
        service = HousekeepingService(db)
        task    = service.get_by_id(task_id)
        if not task:
            flash("Không tìm thấy công việc.", "danger")
            return redirect(url_for("housekeeping.list_tasks"))

        rooms = RoomService(db).get_all()
        staff = UserService(db).get_all_users()

        if request.method == "POST":
            assigned_to_id = request.form.get("assigned_to_id", "")
            task_type      = request.form.get("task_type", "")
            description    = request.form.get("description", "").strip()
            scheduled_at   = request.form.get("scheduled_at", "")
            priority       = request.form.get("priority", "normal")

            updated, error = service.update(
                task_id, task_type, description, scheduled_at,
                priority, assigned_to_id, session.get("role", "staff")
            )
            if error:
                flash(error, "danger")
            else:
                flash(f"Đã cập nhật công việc #{updated.TaskID}", "success")
                return redirect(url_for("housekeeping.list_tasks"))
    finally:
        db.close()

    return render_template("housekeeping/form.html",
                           task=task, rooms=rooms, staff=staff,
                           task_types=VALID_TASK_TYPES,
                           priorities=VALID_PRIORITIES,
                           action="Cập nhật công việc")


# ── N1-9: Cập nhật trạng thái công việc ───────────────────────────────
@housekeeping_bp.route("/housekeeping/<int:task_id>/status", methods=["POST"])
@login_required
def update_task_status(task_id):
    new_status = request.form.get("status", "")
    db = SessionLocal()
    try:
        service = HousekeepingService(db)
        _, error = service.update_status(
            task_id, new_status, session["user_id"], session.get("role", "staff")
        )
        if error:
            flash(error, "danger")
        else:
            labels = {
                "pending": "Chờ xử lý",
                "in_progress": "Đang thực hiện",
                "done": "Hoàn thành",
                "cancelled": "Đã huỷ"
            }
            flash(f"Trạng thái công việc: {labels.get(new_status, new_status)}", "success")
    finally:
        db.close()
    return redirect(url_for("housekeeping.list_tasks"))


@housekeeping_bp.route("/housekeeping/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    db = SessionLocal()
    try:
        ok, error = HousekeepingService(db).delete(task_id, session.get("role", "staff"))
        flash("Đã xóa công việc." if ok else error, "success" if ok else "danger")
    finally:
        db.close()
    return redirect(url_for("housekeeping.list_tasks"))
