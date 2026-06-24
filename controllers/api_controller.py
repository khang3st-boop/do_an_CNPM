"""
api_controller.py
=================
JSON API endpoints cho React frontend.
Tất cả route có prefix /api/ và trả về JSON.
Xác thực qua Flask session (dùng chung với login Flask hiện có).
"""
from flask import Blueprint, jsonify, request, session
from database.connection import SessionLocal
from services.room_service import RoomService, VALID_TYPES, VALID_STATUSES
from services.user_service import UserService
from services.auth_service import AuthService
from services.reminder_service import ReminderService
from services.housekeeping_service import HousekeepingService
from functools import wraps

api_bp = Blueprint("api", __name__, url_prefix="/api")


# ── Helpers ──────────────────────────────────────────────────────────

def api_login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Chưa đăng nhập"}), 401
        return f(*args, **kwargs)
    return decorated


def api_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"success": False, "message": "Chưa đăng nhập"}), 401
        if session.get("role") not in ("admin", "manager"):
            return jsonify({"success": False, "message": "Không có quyền truy cập"}), 403
        return f(*args, **kwargs)
    return decorated


def serialize_maintenance_task(task):
    room = getattr(task, "room", None)
    assigned_to = getattr(task, "assigned_to", None)
    return {
        "id": task.TaskID,
        "room_id": task.RoomID,
        "room_number": getattr(room, "RoomNumber", None),
        "assigned_to_id": task.AssignedToID,
        "assigned_to_name": (
            getattr(assigned_to, "FullName", None)
            or getattr(assigned_to, "Username", None)
        ),
        "task_type": task.TaskType,
        "status": task.Status,
        "priority": task.Priority,
        "description": task.Description or "",
        "result_note": getattr(task, "ResultNote", "") or "",
        "scheduled_at": task.ScheduledAt.isoformat() if task.ScheduledAt else None,
        "completed_at": task.CompletedAt.isoformat() if task.CompletedAt else None,
        "created_at": task.CreatedAt.isoformat() if task.CreatedAt else None,
    }


# ── Auth ─────────────────────────────────────────────────────────────

@api_bp.route("/auth/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    # Hỗ trợ login bằng username hoặc email
    login_key = username or email

    db = SessionLocal()
    try:
        service = AuthService(db)
        # Thử login bằng username trước
        user = service.login(login_key, password)
        if not user and email:
            # Nếu không thấy theo username, thử tìm user theo email rồi login
            from repositories.user_repository import UserRepository
            repo = UserRepository(db)
            all_users = repo.get_all()
            matched = next((u for u in all_users if getattr(u, "Email", "") == email), None)
            if matched:
                user = service.login(matched.Username, password)

        if user:
            session["user_id"]  = user.UserID
            session["username"] = user.Username
            session["role"]     = user.Role
            session["department"] = getattr(user, "Department", "general")
            return jsonify({
                "success": True,
                "data": {
                    "token": f"session-{user.UserID}",  # Placeholder; dùng session cookie
                    "user": {
                        "id":       user.UserID,
                        "username": user.Username,
                        "email":    getattr(user, "Email", ""),
                        "role":     user.Role,
                        "department": getattr(user, "Department", "general"),
                    }
                }
            })
        return jsonify({"success": False, "message": "Sai tên đăng nhập hoặc mật khẩu"}), 401
    finally:
        db.close()


@api_bp.route("/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True})


@api_bp.route("/auth/me")
@api_login_required
def api_me():
    return jsonify({
        "success": True,
        "data": {
            "id":       session["user_id"],
            "username": session["username"],
            "role":     session["role"],
            "department": session.get("department", "general"),
        }
    })


# ── Rooms ─────────────────────────────────────────────────────────────

@api_bp.route("/rooms")
@api_login_required
def api_list_rooms():
    status_filter = request.args.get("status", "")
    db = SessionLocal()
    try:
        service = RoomService(db)
        rooms = service.get_by_status(status_filter) if status_filter else service.get_all()
        data = []
        for r in rooms:
            # Map trạng thái tiếng Việt → tiếng Anh cho React
            status_map = {
                "Trống": "available",
                "Đang ở": "occupied",
                "Bảo trì": "maintenance",
            }
            data.append({
                "id":             r.RoomID,
                "room_number":    r.RoomNumber,
                "room_type":      r.RoomType,
                "floor":          r.Floor,
                "status":         status_map.get(r.Status, r.Status),
                "description":    getattr(r, "Description", ""),
                "price_per_night": 0,  # Thêm trường giá nếu model có
            })
        return jsonify({"success": True, "data": data})
    finally:
        db.close()


@api_bp.route("/rooms/<int:room_id>")
@api_login_required
def api_get_room(room_id):
    db = SessionLocal()
    try:
        service = RoomService(db)
        r = service.get_by_id(room_id)
        if not r:
            return jsonify({"success": False, "message": "Không tìm thấy phòng"}), 404
        status_map = {"Trống": "available", "Đang ở": "occupied", "Bảo trì": "maintenance"}
        return jsonify({"success": True, "data": {
            "id": r.RoomID, "room_number": r.RoomNumber, "room_type": r.RoomType,
            "floor": r.Floor, "status": status_map.get(r.Status, r.Status),
        }})
    finally:
        db.close()


@api_bp.route("/rooms", methods=["POST"])
@api_admin_required
def api_create_room():
    data = request.get_json() or {}
    db = SessionLocal()
    try:
        service = RoomService(db)
        room, error = service.create(
            data.get("room_number", ""),
            data.get("room_type", ""),
            data.get("floor", 1),
            data.get("description", "")
        )
        if error:
            return jsonify({"success": False, "message": error}), 400
        return jsonify({"success": True, "data": {"id": room.RoomID, "room_number": room.RoomNumber}}), 201
    finally:
        db.close()


@api_bp.route("/rooms/<int:room_id>", methods=["PATCH"])
@api_admin_required
def api_update_room(room_id):
    data = request.get_json() or {}
    db = SessionLocal()
    try:
        service = RoomService(db)
        # Map English status back to Vietnamese
        status_remap = {"available": "Trống", "occupied": "Đang ở", "maintenance": "Bảo trì"}
        status = data.get("status")
        if status:
            status = status_remap.get(status, status)
        updated, error = service.update(
            room_id,
            room_type=data.get("room_type"),
            status=status,
            floor=data.get("floor"),
            description=data.get("description")
        )
        if error:
            return jsonify({"success": False, "message": error}), 400
        return jsonify({"success": True, "data": {"id": updated.RoomID}})
    finally:
        db.close()


@api_bp.route("/rooms/<int:room_id>", methods=["DELETE"])
@api_admin_required
def api_delete_room(room_id):
    db = SessionLocal()
    try:
        service = RoomService(db)
        ok, error = service.delete(room_id, session.get("role", "staff"))
        if ok:
            return jsonify({"success": True})
        return jsonify({"success": False, "message": error}), 400
    finally:
        db.close()


# ── Users / Accounts ─────────────────────────────────────────────────

@api_bp.route("/users")
@api_admin_required
def api_list_users():
    keyword = request.args.get("keyword", "")
    role_filter = request.args.get("role", "")
    status_filter = request.args.get("status_filter", "")

    db = SessionLocal()
    try:
        service = UserService(db)
        users = service.get_all_users()
        data = []
        for u in users:
            name = getattr(u, "FullName", None) or u.Username
            email = getattr(u, "Email", "")
            role = u.Role
            status = getattr(u, "Status", "active") or "active"
            dept = getattr(u, "Department", "") or "general"

            # Áp bộ lọc
            if keyword and keyword.lower() not in name.lower() and keyword.lower() not in email.lower():
                continue
            if role_filter and role != role_filter:
                continue
            if status_filter and status != status_filter:
                continue

            data.append({
                "id":         u.UserID,
                "name":       name,
                "email":      email,
                "role":       role,
                "department": dept,
                "phone":      getattr(u, "Phone", ""),
                "status":     status,
            })
        return jsonify({"success": True, "data": data})
    finally:
        db.close()


@api_bp.route("/users", methods=["POST"])
@api_admin_required
def api_create_user():
    data = request.get_json() or {}
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        # Dùng name làm username nếu không có
        username = data.get("name", "").strip().replace(" ", "_").lower()
        user, error = auth_service.create_user(
            username,
            data.get("password", ""),
            data.get("email", ""),
            data.get("role", "staff"),
            data.get("department", "reception")
        )
        if error:
            return jsonify({"success": False, "message": error}), 400
        return jsonify({"success": True, "data": {"id": user.UserID, "username": user.Username}}), 201
    finally:
        db.close()


@api_bp.route("/users/<int:user_id>/toggle-status", methods=["PATCH"])
@api_admin_required
def api_toggle_user_status(user_id):
    """
    Model User hiện tại không có cột Status.
    Endpoint này trả về phản hồi giả lập để giao diện React hoạt động.
    Khi bạn thêm cột Status vào model, uncomment phần cập nhật thật.
    """
    db = SessionLocal()
    try:
        service = UserService(db)
        user, error = service.toggle_status(user_id, session["user_id"], session.get("role", "staff"))
        if error:
            return jsonify({"success": False, "message": error}), 400
        return jsonify({"success": True, "data": {"status": user.Status}})
        user = service.get_user_by_id(user_id)
        if not user:
            return jsonify({"success": False, "message": "Không tìm thấy tài khoản"}), 404
        # Nếu model chưa có Status, dùng in-memory toggle (demo)
        # Để tích hợp thật: thêm cột Status vào bảng Users rồi update ở đây
        return jsonify({"success": True, "data": {"status": "locked", "message": "Cần thêm cột Status vào model User để lưu thật"}})
    finally:
        db.close()


# ── Reminders ─────────────────────────────────────────────────────────

@api_bp.route("/reminders")
@api_login_required
def api_list_reminders():
    db = SessionLocal()
    try:
        service = ReminderService(db)
        reminders = service.get_all(session["user_id"])
        data = [{
            "id":            r.ReminderID,
            "title":         r.Title,
            "description":   r.Description or "",
            "reminder_time": r.ReminderTime.isoformat() if r.ReminderTime else None,
            "status":        r.Status,
        } for r in reminders]
        return jsonify({"success": True, "data": data})
    finally:
        db.close()


# Maintenance schedules API

def _normalize_scheduled_at(value):
    if value is None:
        return ""
    text = str(value).strip()
    if len(text) >= 16:
        text = text.replace(" ", "T", 1)
        return text[:16]
    return text


@api_bp.route("/maintenance-schedules")
@api_login_required
def api_list_maintenance_schedules():
    status_filter = request.args.get("status", "").strip()
    room_id = request.args.get("room_id", "").strip()
    assigned_to_id = request.args.get("assigned_to_id", "").strip()

    db = SessionLocal()
    try:
        service = HousekeepingService(db)
        role = session.get("role", "staff")
        if role == "staff":
            tasks = service.get_by_staff(session["user_id"])
            if status_filter:
                tasks = [t for t in tasks if t.Status == status_filter]
        else:
            tasks = service.get_by_status(status_filter) if status_filter else service.get_all()

        tasks = [t for t in tasks if t.TaskType == "maintenance"]
        if room_id:
            tasks = [t for t in tasks if str(t.RoomID) == room_id]
        if assigned_to_id:
            tasks = [t for t in tasks if str(t.AssignedToID or "") == assigned_to_id]

        return jsonify({"success": True, "data": [serialize_maintenance_task(t) for t in tasks]})
    finally:
        db.close()


@api_bp.route("/maintenance-schedules/<int:task_id>")
@api_login_required
def api_get_maintenance_schedule(task_id):
    db = SessionLocal()
    try:
        task = HousekeepingService(db).get_by_id(task_id)
        if not task or task.TaskType != "maintenance":
            return jsonify({"success": False, "message": "Khong tim thay lich bao tri phong"}), 404
        return jsonify({"success": True, "data": serialize_maintenance_task(task)})
    finally:
        db.close()


@api_bp.route("/maintenance-schedules", methods=["POST"])
@api_admin_required
def api_create_maintenance_schedule():
    data = request.get_json() or {}
    room_id = data.get("room_id")
    scheduled_at = _normalize_scheduled_at(data.get("scheduled_at"))

    if not room_id:
        return jsonify({"success": False, "message": "room_id la bat buoc"}), 400

    db = SessionLocal()
    try:
        service = HousekeepingService(db)
        task, error = service.create(
            int(room_id),
            data.get("assigned_to_id"),
            "maintenance",
            data.get("description", ""),
            scheduled_at,
            data.get("priority", "normal"),
            session.get("role", "staff"),
        )
        if error:
            return jsonify({"success": False, "message": error}), 400
        return jsonify({"success": True, "data": serialize_maintenance_task(task)}), 201
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "room_id khong hop le"}), 400
    finally:
        db.close()


@api_bp.route("/maintenance-schedules/<int:task_id>", methods=["PATCH"])
@api_admin_required
def api_update_maintenance_schedule(task_id):
    data = request.get_json() or {}

    db = SessionLocal()
    try:
        service = HousekeepingService(db)
        task = service.get_by_id(task_id)
        if not task or task.TaskType != "maintenance":
            return jsonify({"success": False, "message": "Khong tim thay lich bao tri phong"}), 404

        room_id = data.get("room_id", task.RoomID)
        scheduled_at = _normalize_scheduled_at(
            data.get("scheduled_at", task.ScheduledAt.strftime("%Y-%m-%dT%H:%M"))
        )
        assigned_to_id = data.get("assigned_to_id", task.AssignedToID)
        priority = data.get("priority", task.Priority)
        description = data.get("description", task.Description or "")

        updated, error = service.update(
            task_id,
            "maintenance",
            description,
            scheduled_at,
            priority,
            assigned_to_id,
            session.get("role", "staff"),
            room_id=int(room_id),
            result_note=data.get("result_note"),
        )
        if error:
            return jsonify({"success": False, "message": error}), 400

        status = data.get("status")
        if status is not None:
            updated, error = service.update_status(
                task_id,
                status,
                session["user_id"],
                session.get("role", "staff"),
                data.get("result_note"),
            )
            if error:
                return jsonify({"success": False, "message": error}), 400

        return jsonify({"success": True, "data": serialize_maintenance_task(updated)})
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "room_id khong hop le"}), 400
    finally:
        db.close()


@api_bp.route("/maintenance-schedules/<int:task_id>", methods=["DELETE"])
@api_admin_required
def api_delete_maintenance_schedule(task_id):
    hard_delete = request.args.get("hard_delete", "").lower() in ("1", "true", "yes")

    db = SessionLocal()
    try:
        service = HousekeepingService(db)
        task = service.get_by_id(task_id)
        if not task or task.TaskType != "maintenance":
            return jsonify({"success": False, "message": "Khong tim thay lich bao tri phong"}), 404

        if hard_delete:
            ok, error = service.delete(task_id, session.get("role", "staff"))
            if not ok:
                return jsonify({"success": False, "message": error}), 400
            return jsonify({"success": True})

        updated, error = service.update_status(
            task_id,
            "cancelled",
            session["user_id"],
            session.get("role", "staff"),
        )
        if error:
            return jsonify({"success": False, "message": error}), 400
        return jsonify({"success": True, "data": serialize_maintenance_task(updated)})
    finally:
        db.close()
