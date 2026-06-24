from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from database.connection import SessionLocal
from services.user_service import UserService
from services.auth_service import AuthService
from functools import wraps

user_bp = Blueprint("user", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """N1-13: Chỉ admin mới truy cập được."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Bạn không có quyền truy cập trang này.", "danger")
            return redirect(url_for("reminder.dashboard"))
        return f(*args, **kwargs)
    return decorated


# ── N1-12: Danh sách nhân viên ──────────────────────────────────────
@user_bp.route("/users")
@login_required
@admin_required
def list_users():
    db = SessionLocal()
    try:
        service = UserService(db)
        users = service.get_all_users()
    finally:
        db.close()
    return render_template("users/list.html", users=users)


# ── N1-12: Thêm nhân viên ───────────────────────────────────────────
@user_bp.route("/users/create", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        email    = request.form.get("email", "").strip()
        role     = request.form.get("role", "staff")

        db = SessionLocal()
        try:
            auth_service = AuthService(db)
            user, error = auth_service.create_user(username, password, email, role)
            if error:
                flash(error, "danger")
            else:
                flash(f"Đã tạo tài khoản: {user.Username}", "success")
                return redirect(url_for("user.list_users"))
        finally:
            db.close()

    return render_template("users/form.html", user=None, action="Thêm nhân viên")


# ── N1-12: Cập nhật nhân viên ───────────────────────────────────────
@user_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(user_id):
    db = SessionLocal()
    try:
        service = UserService(db)
        user = service.get_user_by_id(user_id)
        if not user:
            flash("Không tìm thấy tài khoản.", "danger")
            return redirect(url_for("user.list_users"))

        if request.method == "POST":
            email        = request.form.get("email", "").strip()
            role         = request.form.get("role", "")
            new_password = request.form.get("new_password", "").strip()

            updated, error = service.update_user(
                user_id,
                email=email or None,
                role=role or None,
                new_password=new_password or None,
                current_user_role=session.get("role", "staff")
            )
            if error:
                flash(error, "danger")
            else:
                flash(f"Đã cập nhật tài khoản: {updated.Username}", "success")
                return redirect(url_for("user.list_users"))
    finally:
        db.close()

    return render_template("users/form.html", user=user, action="Cập nhật nhân viên")


# ── N1-12: Xóa nhân viên ────────────────────────────────────────────
@user_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    db = SessionLocal()
    try:
        service = UserService(db)
        ok, error = service.delete_user(user_id, session["user_id"], session.get("role"))
        if ok:
            flash("Đã xóa tài khoản.", "success")
        else:
            flash(error, "danger")
    finally:
        db.close()
    return redirect(url_for("user.list_users"))
