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
            return jsonify({
                "success": True,
                "data": {
                    "token": f"session-{user.UserID}",  # Placeholder; dùng session cookie
                    "user": {
                        "id":       user.UserID,
                        "username": user.Username,
                        "email":    getattr(user, "Email", ""),
                        "role":     user.Role,
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
            dept_map = {
                "admin": "management",
                "manager": "management",
                "staff": "reception",
                "receptionist": "reception",
                "housekeeping": "housekeeping",
            }
            dept = dept_map.get(role, "general")

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
            data.get("role", "staff")
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
